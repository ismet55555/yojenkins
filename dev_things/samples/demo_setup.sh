
yojenkins folder create --type folder "Dev Jobs" . --debug
yojenkins job create "Test" "Dev Jobs"
yojenkins job create "Build" "Dev Jobs" --config "./dev_things/samples/job_config/limited_loop.xml"

yojenkins folder create --type folder "Prod Jobs" .
yojenkins job create "Release" "Dev Jobs" --config "./dev_things/samples/job_config/simple_datetime.xml"
yojenkins job create "Monitor" "Dev Jobs" --config "./dev_things/samples/job_config/limited_loop.xml"

yojenkins job build "Dev Jobs/Test"
yojenkins job build "Dev Jobs/Build"
