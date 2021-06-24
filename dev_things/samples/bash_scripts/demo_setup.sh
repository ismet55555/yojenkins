yo-jenkins folder create --type folder "Dev Jobs" .
yo-jenkins job create "Test" "Dev Jobs"
yo-jenkins job create "Build" "Dev Jobs" --config .\dev_things\samples\job_config\limited_loop.xml

yo-jenkins folder create --type folder "Prod Jobs" .
yo-jenkins job create "Release" "Dev Jobs" --config .\dev_things\samples\job_config\simple_datetime.xml
yo-jenkins job create "Monitor" "Dev Jobs" --config .\dev_things\samples\job_config\limited_loop.xml

yo-jenkins job build "Dev Jobs/Test"
yo-jenkins job build "Dev Jobs/Build"

