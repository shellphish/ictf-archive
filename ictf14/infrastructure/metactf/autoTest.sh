for d in $(./serviceDirs); do
  cd $d
  echo $d
  ../../tester.py info.json $1|grep SUCCESS
  cd ../../
done
