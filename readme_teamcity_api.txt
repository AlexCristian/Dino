“XML combines the efficiency of text files with the readability of binary files” — unknown
That being said, herein lies a recounting of my time spent wrapping my head around the TeamCity Web API.

http://url:port/httpAuth/app/rest/builds/?locator=buildType:(id:YOUR_PROJECT_ID)&guest=1
--> dumps an XML with the project's builds + build status

We can also modify the request to only return an XML with the latest 5 builds
http://url:port/httpAuth/app/rest/builds/?locator=buildType:(id:YOUR_PROJECT_ID)&count=5&guest=1

Furthermore, we can then go on to extract our desired build's ID. We'll then paste it into the following request:
http://url:port/httpAuth/app/rest/changes?build=id:YOUR_BUILD_ID
which will return us a new XML with the new changes implemented in this build. Pick one and use the "href" argument to finally
arrive at something like this:
http://url:port/httpAuth/app/rest/changes/id:YOUR_CHANGE_ID
that joyfully spits out the entire commit details in their full XML glory.



A final word on the '&guest=1' part of the request. The API will sometimes arbitrarily refuse to respond to a query
if you fail to identify yourself as a guest, depending on what information you're asking for. 