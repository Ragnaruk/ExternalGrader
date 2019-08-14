cd "../../working_directory" || exit 101

(( grade = 0 ))

if [ "$(cat test.txt)" == "Hello World" ]; then
  (( grade += 50 ))
fi

if [ "$(cat hello_world.txt)" == "" ]; then
  (( grade += 50 ))
fi

echo "$grade"
exit 0