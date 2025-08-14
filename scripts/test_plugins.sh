
#!/bin/bash

directory="plugins"

for dir in "$directory"/*; do
    if [ -d "$dir" ]; then
        echo "pytest: $dir"
        cd $dir
        poetry run pytest
        cd -
    fi
done
