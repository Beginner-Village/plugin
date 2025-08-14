
#!/bin/bash

directory="plugins"

for dir in "$directory"/*; do
    if [ -d "$dir" ]; then
        echo "build: $dir"
        poetry run python -m build -w $dir -o dist -n
    fi
done
