# coding=utf-8

"""
requires Python 3.6 or later

pip install asyncio
pip install websockets
"""
from typing import Tuple
import asyncio
import base64
import gzip
import hmac
import json
import logging
import os
import uuid
import wave
from enum import Enum
from hashlib import sha256
from io import BytesIO
from typing import List
from urllib.parse import urlparse
import time
import websockets

PROTOCOL_VERSION = 0b0001
DEFAULT_HEADER_SIZE = 0b0001

PROTOCOL_VERSION_BITS = 4
HEADER_BITS = 4
MESSAGE_TYPE_BITS = 4
MESSAGE_TYPE_SPECIFIC_FLAGS_BITS = 4
MESSAGE_SERIALIZATION_BITS = 4
MESSAGE_COMPRESSION_BITS = 4
RESERVED_BITS = 8

# Message Type:
CLIENT_FULL_REQUEST = 0b0001
CLIENT_AUDIO_ONLY_REQUEST = 0b0010
SERVER_FULL_RESPONSE = 0b1001
SERVER_ACK = 0b1011
SERVER_ERROR_RESPONSE = 0b1111

# Message Type Specific Flags
NO_SEQUENCE = 0b0000  # no check sequence
POS_SEQUENCE = 0b0001
NEG_SEQUENCE = 0b0010
NEG_SEQUENCE_1 = 0b0011

# Message Serialization
NO_SERIALIZATION = 0b0000
JSON = 0b0001
THRIFT = 0b0011
CUSTOM_TYPE = 0b1111

# Message Compression
NO_COMPRESSION = 0b0000
GZIP = 0b0001
CUSTOM_COMPRESSION = 0b1111


def generate_header(
    version=PROTOCOL_VERSION,
    message_type=CLIENT_FULL_REQUEST,
    message_type_specific_flags=NO_SEQUENCE,
    serial_method=JSON,
    compression_type=GZIP,
    reserved_data=0x00,
    extension_header=bytes()
):
    """
    protocol_version(4 bits), header_size(4 bits),
    message_type(4 bits), message_type_specific_flags(4 bits)
    serialization_method(4 bits) message_compression(4 bits)
    reserved （8bits) 保留字段
    header_extensions 扩展头(大小等于 8 * 4 * (header_size - 1) )
    """
    header = bytearray()
    header_size = int(len(extension_header) / 4) + 1
    header.append((version << 4) | header_size)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serial_method << 4) | compression_type)
    header.append(reserved_data)
    header.extend(extension_header)
    return header


def generate_full_default_header():
    return generate_header()


def generate_audio_default_header():
    return generate_header(
        message_type=CLIENT_AUDIO_ONLY_REQUEST
    )


def generate_last_audio_default_header():
    return generate_header(
        message_type=CLIENT_AUDIO_ONLY_REQUEST,
        message_type_specific_flags=NEG_SEQUENCE
    )


def parse_response(res):
    """
    protocol_version(4 bits), header_size(4 bits),
    message_type(4 bits), message_type_specific_flags(4 bits)
    serialization_method(4 bits) message_compression(4 bits)
    reserved （8bits) 保留字段
    header_extensions 扩展头(大小等于 8 * 4 * (header_size - 1) )
    payload 类似与http 请求体
    """
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f
    serialization_method = res[2] >> 4
    message_compression = res[2] & 0x0f
    reserved = res[3]
    header_extensions = res[4:header_size * 4]
    payload = res[header_size * 4:]
    result = {}
    payload_msg = None
    payload_size = 0
    if message_type == SERVER_FULL_RESPONSE:
        payload_size = int.from_bytes(payload[:4], "big", signed=True)
        payload_msg = payload[4:]
    elif message_type == SERVER_ACK:
        seq = int.from_bytes(payload[:4], "big", signed=True)
        result['seq'] = seq
        if len(payload) >= 8:
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:]
    elif message_type == SERVER_ERROR_RESPONSE:
        code = int.from_bytes(payload[:4], "big", signed=False)
        result['code'] = code
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        payload_msg = payload[8:]
    if payload_msg is None:
        return result
    if message_compression == GZIP:
        payload_msg = gzip.decompress(payload_msg)
    if serialization_method == JSON:
        payload_msg = json.loads(str(payload_msg, "utf-8"))
    elif serialization_method != NO_SERIALIZATION:
        payload_msg = str(payload_msg, "utf-8")
    result['payload_msg'] = payload_msg
    result['payload_size'] = payload_size
    return result


def read_wav_info(data: bytes):
    with BytesIO(data) as _f:
        wave_fp = wave.open(_f, 'rb')
        nchannels, sampwidth, framerate, nframes = wave_fp.getparams()[:4]
        wave_bytes = wave_fp.readframes(nframes)
    return nchannels, sampwidth, framerate, nframes, len(wave_bytes)


class AudioType(Enum):
    LOCAL = 1  # 使用本地音频文件


class AsrWsClient:
    def __init__(self, audio_path, cluster, **kwargs):
        """
        :param config: config
        """
        self.audio_path = audio_path
        self.cluster = cluster
        self.success_code = 1000  # success code, default is 1000
        self.seg_duration = int(kwargs.get("seg_duration", 15000))
        self.nbest = int(kwargs.get("nbest", 1))
        self.appid = kwargs.get("appid", "")
        self.token = kwargs.get("token", "")
        self.ws_url = kwargs.get(
            "ws_url", "wss://openspeech.bytedance.com/api/v2/asr")
        self.uid = kwargs.get("uid", "streaming_asr_demo")
        self.workflow = kwargs.get(
            "workflow", "audio_in,resample,partition,vad,fe,decode,itn,nlu_punctuate")
        self.show_language = kwargs.get("show_language", False)
        self.show_utterances = kwargs.get("show_utterances", False)
        self.result_type = kwargs.get("result_type", "full")
        self.format = kwargs.get("format", "wav")
        self.rate = kwargs.get("sample_rate", 16000)
        self.language = kwargs.get("language", "zh-CN")
        self.bits = kwargs.get("bits", 16)
        self.channel = kwargs.get("channel", 1)
        self.codec = kwargs.get("codec", "raw")
        self.audio_type = kwargs.get("audio_type", AudioType.LOCAL)
        self.secret = kwargs.get("secret", "access_secret")
        self.auth_method = kwargs.get("auth_method", "token")
        self.mp3_seg_size = int(kwargs.get("mp3_seg_size", 10000))

    def construct_request(self, reqid):
        req = {
            'app': {
                'appid': self.appid,
                'cluster': self.cluster,
                'token': self.token,
            },
            'user': {
                'uid': self.uid
            },
            'request': {
                'reqid': reqid,
                'nbest': self.nbest,
                'workflow': self.workflow,
                'show_language': self.show_language,
                'show_utterances': self.show_utterances,
                'result_type': self.result_type,
                "sequence": 1
            },
            'audio': {
                'format': self.format,
                'rate': self.rate,
                'language': self.language,
                'bits': self.bits,
                'channel': self.channel,
                'codec': self.codec
            }
        }
        return req

    @staticmethod
    def slice_data(data: bytes, chunk_size: int):
        """
        slice data
        :param data: wav data
        :param chunk_size: the segment size in one request
        :return: segment data, last flag
        """
        data_len = len(data)
        offset = 0
        while offset + chunk_size < data_len:
            yield data[offset: offset + chunk_size], False
            offset += chunk_size
        else:
            yield data[offset: data_len], True

    # def _real_processor(self, request_params: dict) -> dict:
    #     pass

    def token_auth(self):
        return {'Authorization': 'Bearer; {}'.format(self.token)}

    def signature_auth(self, data):
        header_dicts = {
            'Custom': 'auth_custom',
        }

        url_parse = urlparse(self.ws_url)
        input_str = 'GET {} HTTP/1.1\n'.format(url_parse.path)
        auth_headers = 'Custom'
        for header in auth_headers.split(','):
            input_str += '{}\n'.format(header_dicts[header])
        input_data = bytearray(input_str, 'utf-8')
        input_data += data
        mac = base64.urlsafe_b64encode(
            hmac.new(self.secret.encode('utf-8'), input_data, digestmod=sha256).digest())
        header_dicts['Authorization'] = 'HMAC256; access_token="{}"; mac="{}"; h="{}"'.format(
            self.token, str(mac, 'utf-8'), auth_headers)
        return header_dicts

    async def segment_data_processor(self, wav_data: bytes, segment_size: int):
        reqid = str(uuid.uuid4())
        # 构建 full client request，并序列化压缩
        request_params = self.construct_request(reqid)
        payload_bytes = str.encode(json.dumps(request_params))
        payload_bytes = gzip.compress(payload_bytes)
        full_client_request = bytearray(generate_full_default_header())
        full_client_request.extend((len(payload_bytes)).to_bytes(
            4, 'big'))  # payload size(4 bytes)
        full_client_request.extend(payload_bytes)  # payload
        header = None
        if self.auth_method == "token":
            header = self.token_auth()
        elif self.auth_method == "signature":
            header = self.signature_auth(full_client_request)
        async with websockets.connect(self.ws_url, additional_headers=header, max_size=1000000000) as ws:
            # 发送 full client request
            await ws.send(full_client_request)
            res = await ws.recv()
            result = parse_response(res)
            if 'payload_msg' in result and result['payload_msg']['code'] != self.success_code:
                return result
            for seq, (chunk, last) in enumerate(AsrWsClient.slice_data(wav_data, segment_size), 1):
                # if no compression, comment this line
                payload_bytes = gzip.compress(chunk)
                audio_only_request = bytearray(generate_audio_default_header())
                if last:
                    audio_only_request = bytearray(
                        generate_last_audio_default_header())
                audio_only_request.extend((len(payload_bytes)).to_bytes(
                    4, 'big'))  # payload size(4 bytes)
                audio_only_request.extend(payload_bytes)  # payload
                # 发送 audio-only client request
                await ws.send(audio_only_request)
                res = await ws.recv()
                result = parse_response(res)
                # print(f"seq: {seq}, result: {result}")
                if 'payload_msg' in result and result['payload_msg']['code'] != self.success_code:
                    return result
        return result

    async def execute(self):
        with open(self.audio_path, mode="rb") as _f:
            data = _f.read()
        audio_data = bytes(data)
        match self.format:
            case "wav":
                nchannels, sampwidth, framerate, nframes, wav_len = read_wav_info(
                    audio_data)
                size_per_sec = nchannels * sampwidth * framerate
                segment_size = int(size_per_sec * self.seg_duration / 1000)
            case _:
                segment_size = self.mp3_seg_size
        return await self.segment_data_processor(audio_data, segment_size)


def execute_one(audio_item, cluster, **kwargs):
    """
    :param audio_item: {"id": xxx, "path": "xxx"}
    :param cluster:集群名称
    :return: {'payload_msg': {'addition': {'duration': '3264', 'logid': '20241125112235CACC2F564CDCB4F63A3C', 'split_time': '[]'}, 'code': 1000, 'message': 'Success', 'reqid': 'b25be66b-0cde-4af2-ae14-34458e91c06e', 'result': [{'confidence': 0, 'text': '测试语音识别。'}], 'sequence': -4}, 'payload_size': 237}
    :return: {'payload_msg': {'addition': {'duration': '839160', 'logid': '202411251124285FCEC7B0FA7467D75B1F', 'split_time': '[]'}, 'code': 1000, 'message': 'Success', 'reqid': '226d1f62-bd10-4b46-acf9-67fab5e9ce14', 'result': [{'confidence': 0, 'text': '从今天起， 我为朋友们讲述中国的古典名著红楼梦。 这波红楼梦从何处而来呢？ 要说起他的根由来，好像很荒唐。 可是你听过之后，细细的品味，却深有趣味。 原来自女娲娘娘练食补天的时候。 就在大荒山，无耻！ 牙练成了顽石36,501块。 可是娘娘补天只用了36,500块，剩下一块没用。 就把这块石头扔在了这座山的青梗峰下。 这块石头呢？ 自己经过锻炼之后通了灵性。 石头就想。 所有的石头全都让女娲娘娘。 补了天了！ 唯独自己无才，不能入选，所以石头就自怨自叹，日夜惭愧悲好。 这一天，石头正在伤心，突然间来了一个僧人，来了一个道长。 两位仙师生的骨骼不凡，封神迥异，说说笑笑就来到了封下坐在这块石头旁边高度。 谈快乐！ 先是说了些云山雾海，神仙玄幻之势，然后就说到红尘中的荣华富贵。 这块石头听了，不觉打动了凡心，就口吐人言跟这二位仙师说。 大师！ 弟子刚才听二位谈谈人间的荣耀繁华，我十分。 羡慕。 二位大师能不能萌发一点慈心，带着弟子得入红尘，也在那场富贵场中温柔乡里享受几年？ 我赐当永佩红恩！ 这二位先师听了之后就笑了。 善哉善哉！ 那红尘中确实有些乐事。 但不能永远。 仪式况且又有美中不足。好事多磨8个字紧紧相连。 瞬息间则有乐极生悲。 人非物坏，究竟是到头一梦啊！ 万径归空，倒不如不去的好。 这块石头繁星移动了！ 哪里听得进去这样的话，他就再三的。 苦求！ 二位仙长就叹了一口气说。 既如此，我们便带你去受享受享！ 可是要抵到了不得意的时候，千万不要后悔呀！ 石头说啊，自然，自然！ 僧人又说。 要说你同灵性吧！ 你有如此志纯？ 更无奇。 一跪之处也罢，我如今大师佛法助你一柱，待劫中之日复还本质，已了此案。 你看如何呀？ 石头听了是感谢不尽。 僧人叫念咒书服，大展幻术，就把这一块大石头变成了一块鲜明盈拮的美玉玉。 要把它缩成善。 一块大小，僧人就把这块美玉托于手掌之上，哈哈大笑好啊！ 形体倒是个宝物了。 只是没有实在的好处。 嗯，还得在捐上几个字，使人一看就知道是个奇物。 然后好带你到那昌明龙胜之邦，诗里簪英。 知足化了繁华地，温柔富贵乡，却安身乐意。 说完之后就带上这块石头跟这位道人飘飘而去。 那么二位先师就总投奔了何方呢？ 谁也不知道。 后来又不知过了几式几节，有一位空空道人从这大荒山无极牙青耿峰下经过。 看一块大石上自己分明编数立立！ 空空道人从头一看，哦，原来是石头无彩补天，唤醒入室。 萌萌萌，大事渺渺，真人带入红尘，历经离合悲欢颜，良世态的一段故事。 空空岛人就把这石头计从头到。 宝贝，抄录回来！ 后来曹雪芹。 在道宏宣中批阅十载，增山五次。 转成目录，分出张回，并提出了一首绝句。 满指荒唐言，一把辛酸泪。 抖音作者持谁解其中味？ 那么，这石头上说的故事到底是？ 什么呢？ 听我慢慢道来。 想当初，地陷东南。 这东南有座姑苏城，是红尘中上。 富贵风流之地。 顾舒城仓门外十里街人倾向有个古庙，这座古庙呢，叫葫芦庙。 就在庙的旁边，住着一家香浣，这个人姓甄名肺，字是隐。 这位真是尹先生，秉性恬淡。 不图功名，每天就观花修竹，浊酒银饰。 倒是神仙一流人品，如今年已半百，七下无儿，只有一个女儿，乳名银莲，刚刚3岁。 这天言下，涌咒！ 真是引在书房中，就朦朦胧胧的睡着了。 在梦中，他走到一个地方。 没去过。 忽然间来了一个僧人，来了一个道长，一边走一边谈，他就听道人问。 我说。 你带了这蠢物，意欲何往啊？ 僧人笑着回答。 是啊，如今有一段风流公案，正该了结这个风流。 冤家尚未投胎入世，趁此机会就将此蠢物夹带于中，使他去经历经历。 道人有数。 这风流冤孽落于何方何处？是何因果呢？ 僧人笑着说。 此事说来也好笑啊！ 竟是千古未闻的一件汉事！ 在西方里， 银河岸上三生石畔有一株绛珠草。 有一位赤霞宫的神鹰逝者，每天用甘露灌溉他。 所以，这颗酱猪草得以久延岁月。 后来既受天地精华，赋得雨露滋养，酱猪草呢，哎。 他脱去了草台，木质换成人形了。 修成个女子之身。 他终日由于离恨天外，饿了他就吃蜜青果，渴了他就喝这个愁海水。 所以， 这颗酱猪草尚未仇报灌溉之德。 他呢，就郁觉着一段缠绵不尽之意。恰好近日这位神鹰逝者烦心呕赤。 也要下凡造力换元，依然在景换仙子案前挂了号。这位绛珠仙子呢？ 就说出了语录之慧。 也去下世为人，他把一生的眼泪呢，还给这位神鹰逝者，这样就勾出多少风流冤家来陪他们去了解此案此案。 道人听了又说， 还累之？ 说，果然是汉文呢！ 既然如此，你我何不趁此时机也下士去夺渡几个？ 也是一场功德呀！ 僧人说正合我意，你先跟我到警患仙子宫中，把蠢物交给清楚。 真是瘾，听得很明白。 可是不知道僧人说的这蠢物是什么东西？ 就上前十里说。 刚才我听仙师所谈因果，实在人间奇闻。 但不知仙长所讲蠢物是什么东西，能不能让我看看呢？ 僧人瞧了瞧甄世隐， 你要问此物吗？嗯，倒是有一面之缘。说着就取出来递给甄世隐。 甄士隐接过离看，原来是。 是一块美玉，上边卷着通灵宝玉四个字。 后边还有几行小字。 他正想细看僧人说话了。 已到幻境了！ 说着就从真世音手中把这块美玉夺走了。 他跟道人走过了一座很大的石牌坊，这牌坊上是太虚幻境四个大字。 两边又有一副对联。 真是因轻生念。 假作真实真意假。 无微有处，有魂无。 朕是人，看见僧人跟道人过了牌坊，也想跟着过去，刚要银白布，就听见咔啦！ 天空中打了一声霹雳。 就好像山崩地陷， 真是因大叫一声，睁眼再一看，只见烈日炎炎，芭蕉冉冉，哦，原来是南柯一梦。 这一下呢，梦中的事情他就望去了多一半。 珍惜人坐这回想这梦，忽然间呢，就看见隔壁葫芦庙里寄居的一个穷书生叫贾以村的从庙里走出来。 这个。 贾宇村因为进京求取功名，就暂时在庙中安身，每天呢，就靠麦字，靠作文生活。 所以真是眼看着可怜，常常接济他。 真是尹，虽然接济他，并不看不起他。 事业一看就站起身来，把贾宇村让到书房，两个人坐这谈话，正谈着呢，忽然家人进来了。 严老爷，前来拜访您！ 甲与村一开，人家来客人了，赶紧就站起来了。老先生请便晚生常来，稍后何方啊？ 真是因起身谢罪就走出了前厅。 贾雨村一个人在书房翻书解闷。 忽然间听见窗外有一个女子咳嗽的声音。 一村起身往窗外一。 看，原来是一个丫鬟正在那掐花。 这个丫鬟生的，眉目清明。 十人无十分姿色，却有动人之处。 贾乙村不觉得，看呆了。 这个甄家的丫鬟猛地一抬头，见窗里有人看自己，就急忙转身回避。 信说！ 这个人生的好雄壮啊！ 可要这样蓝绿哦！ 一定是我家主人常说的困在庙中的贾峪村吧！ 可是我家主人又说他不是久困之人。 这个女子这么想呢，没想到贾雨村误会了。 贾雨村一看这个丫鬟，回头看了自己两眼，认为这个女子对自己有意。 哎呀。 信说这个女子， 此必是巨眼英豪风尘之己了。 过了一会儿， 小书童儿进来，贾以村赶紧上前问话。'}], 'sequence': -1078}, 'payload_size': 4722}
    """
    assert 'id' in audio_item
    assert 'path' in audio_item
    audio_id = audio_item['id']
    audio_path = audio_item['path']
    audio_type = AudioType.LOCAL
    asr_http_client = AsrWsClient(
        audio_path=audio_path,
        cluster=cluster,
        audio_type=audio_type,
        **kwargs
    )
    result = asyncio.run(asr_http_client.execute())
    return {"id": audio_id, "path": audio_path, "result": result}


def test_one():
    appid = os.getenv("voice2text_appid")  # 项目的 appid
    token = os.getenv("voice2text_token")  # 项目的 token
    cluster = os.getenv("voice2text_cluster")  # 请求的集群
    audio_path = "/Users/bytedance/Desktop/nlp_test/nlp_test.mp3"  # 本地音频路径
    audio_format = "mp3"   # wav 或者 mp3，根据实际音频格式设置
    result = execute_one(
        {
            'id': 1,
            'path': audio_path
        },
        cluster=cluster,
        appid=appid,
        token=token,
        format=audio_format,
    )
    print(result)


if __name__ == '__main__':
    test_one()
