#!/usr/bin/env bash

index=trackerapp/src/graphs/index.js
graphs=$(ls trackerapp/src/graphs | grep json)

[ -f $index ] && rm $index

for f in ${graphs[@]}; do
  echo "import fig${f::- 5} from './$f'" >> $index
done

echo '' >> $index
echo 'const graphs = {' >> $index
for f in ${graphs[@]}; do
  echo "'${f::- 5}':  fig${f::- 5}," >> $index
done
echo '}' >> $index

echo '' >> $index
echo 'export default graphs' >> $index
