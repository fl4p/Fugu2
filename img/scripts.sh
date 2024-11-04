
find . -type f -name "*.png" -exec bash -c 'echo $1 && cwebp "$1" -q 66 -o "${1%.png}".webp' - '{}' \;