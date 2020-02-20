echo $REDIS_HOST > /id
# sleep 60
echo "Starting"
python /app/run.py

pushd /output
echo $OS_OUTPUT_CONTAINER_NAME
for file in $files; do
    echo $file
done


