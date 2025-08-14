from pydantic import BaseModel, Field
from typing import List
from hiagent_plugin_tianyancha.common import timestamp_to_str

class IndustryAll(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    category	String	varchar(255)	国民经济行业分类门类
    categoryBig	String	varchar(255)	国民经济行业分类大类
    categoryMiddle	String	varchar(255)	国民经济行业分类中类
    categorySmall	String	varchar(255)	国民经济行业分类小类
    """
    category: str | None = Field(None, description="国民经济行业分类门类")
    categoryBig: str | None = Field(None, description="国民经济行业分类大类")
    categoryMiddle: str | None = Field(None, description="国民经济行业分类中类")
    categorySmall: str | None = Field(None, description="国民经济行业分类小类")

class CompanyDetailResult(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    percentileScore	Number	万分制	企业评分
    staffNumRange	String	varchar(200)	人员规模
    fromTime	Number	时间戳	经营开始时间
    type	Number	int(1)	法人类型，1 人 2 公司
    bondName	String	varchar(20)	股票名
    id	Number	int(20)	企业id
    isMicroEnt	Number	int(1)	是否是小微企业 0不是 1是
    usedBondName	String	varchar(100)	股票曾用名
    regNumber	String	varchar(31)	注册号
    regCapital	String	varchar(50)	注册资本
    name	String	varchar(255)	企业名
    regInstitute	String	varchar(255)	登记机关
    regLocation	String	varchar(255)	注册地址
    industry	String	varchar(255)	行业
    approvedTime	Number	时间戳	核准时间
    updateTimes	Number	时间戳	更新时间
    socialStaffNum	Number	varchar(50)	参保人数
    tags	String	varchar(255)	企业标签
    taxNumber	String	varchar(255)	纳税人识别号
    businessScope	String	varchar(4091)	经营范围
    property3	String	varchar(255)	英文名
    alias	String	varchar(255)	简称
    orgNumber	String	varchar(31)	组织机构代码
    regStatus	String	varchar(31)	企业状态
    estiblishTime	Number	时间戳	成立日期
    bondType	String	varchar(31)	股票类型
    legalPersonName	String	varchar(120)	法人
    toTime	Number	时间戳	经营结束时间
    actualCapital	String	varchar(50)	实收注册资金
    companyOrgType	String	varchar(127)	企业类型
    base	String	varchar(31)	省份简称
    creditCode	String	varchar(255)	统一社会信用代码
    historyNames	String	varchar(255)	曾用名
    historyNameList	Array		曾用名
        _child	String	varchar(255)
    bondNum	String	varchar(20)	股票号
    regCapitalCurrency	String	varchar(10)	注册资本币种 人民币 美元 欧元 等
    actualCapitalCurrency	String	varchar(10)	实收注册资本币种 人民币 美元 欧元 等
    email	String	varchar(50)	邮箱
    websiteList	String	text	网址
    phoneNumber	String	varchar(255)	企业联系方式
    revokeDate	Number	时间戳	吊销日期
    revokeReason	String	varchar(500)	吊销原因
    cancelDate	Number	时间戳	注销日期
    cancelReason	String	varchar(500)	注销原因
    city	String	varchar(20)	市
    district	String	varchar(20)	区
    industryAll	Object		国民经济行业分类
        category	String	varchar(255)	国民经济行业分类门类
        categoryBig	String	varchar(255)	国民经济行业分类大类
        categoryMiddle	String	varchar(255)	国民经济行业分类中类
        categorySmall	String	varchar(255)	国民经济行业分类小类
    """
    percentileScore: int | None = Field(None, description="万分制")
    staffNumRange: str | None = Field(None, description="人员规模")
    fromTime: str = Field("", description="经营开始时间") # int
    type: int | None = Field(None, description="法人类型，1 人 2 公司")
    bondName: str | None = Field(None, description="股票名")
    id: int | None = Field(None, description="企业id")
    isMicroEnt: int | None = Field(None, description="是否是小微企业 0不是 1是")
    usedBondName: str | None = Field(None, description="股票曾用名")
    regNumber: str | None = Field(None, description="注册号")
    regCapital: str | None = Field(None, description="注册资本")
    name: str | None = Field(None, description="企业名")
    regInstitute: str | None = Field(None, description="登记机关")
    regLocation: str | None = Field(None, description="注册地址")
    industry: str | None = Field(None, description="行业")
    approvedTime: str = Field("", description="核准时间") # int
    updateTimes: str = Field("", description="更新时间") # int
    socialStaffNum: int = Field(0, description="参保人数")
    tags: str | None = Field(None, description="企业标签")
    taxNumber: str | None = Field(None, description="纳税人识别号")
    businessScope: str | None = Field(None, description="经营范围")
    property3: str | None = Field(None, description="英文名")
    alias: str | None = Field(None, description="简称")
    orgNumber: str | None = Field(None, description="组织机构代码")
    regStatus: str | None = Field(None, description="企业状态")
    estiblishTime: str = Field("", description="成立日期") # int
    bondType: str | None = Field(None, description="股票类型")
    legalPersonName: str | None = Field(None, description="法人")
    toTime: str = Field("", description="经营结束时间") # int
    actualCapital: str | None = Field(None, description="实收注册资金")
    companyOrgType: str | None = Field(None, description="企业类型")
    base: str | None = Field(None, description="省份简称")
    creditCode: str | None = Field(None, description="统一社会信用代码")
    historyNames: str | None = Field(None, description="曾用名")
    historyNameList: List[str] | None = Field(None, description="曾用名")
    bondNum: str | None = Field(None, description="股票号")
    regCapitalCurrency: str | None = Field(None, description="注册资本币种 人民币 美元 欧元 等")
    actualCapitalCurrency: str | None = Field(None, description="实收注册资本币种 人民币 美元 欧元 等")
    email: str | None = Field(None, description="邮箱")
    websiteList: str | None = Field(None, description="网址")
    phoneNumber: str | None = Field(None, description="企业联系方式")
    revokeDate: str = Field("", description="吊销日期") # int
    revokeReason: str | None = Field(None, description="吊销原因")
    cancelDate: str = Field("", description="注销日期") # int
    cancelReason: str | None = Field(None, description="注销原因")
    city: str | None = Field(None, description="市")
    district: str | None = Field(None, description="区")
    industryAll: IndustryAll | None = Field(None, description="国民经济行业分类")

    def __init__(self, **data):
        # 处理时间字段
        for key in ["fromTime", "approvedTime", "updateTimes", "estiblishTime", "toTime", "revokeDate", "cancelDate"]:
            data[key] = timestamp_to_str(data.get(key))
        super().__init__(**data)
