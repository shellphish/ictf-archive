for d in $(./serviceDirs); do
  cd $d
  ../../autopackage.py>/dev/null 2>/dev/null&
  cd ../../
done
