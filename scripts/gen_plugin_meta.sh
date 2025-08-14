
#!/bin/bash

directory="plugins"

for dir in "$directory"/*; do
    if [ -d "$dir" ]; then
        echo "gen_metadata: $dir"
        cd $dir
        poetry run gen_metadata
        cd -
    fi
done
