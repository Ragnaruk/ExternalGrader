if [[ ! -d "./requirements" ]]; then
  mkdir requirements
  cd ./requirements || exit 1
  echo "Hello World" >> test.txt
fi

exit 0