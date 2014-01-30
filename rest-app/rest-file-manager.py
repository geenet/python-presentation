import bottle
from bottle import route,run,get,request,abort,get,post,put,delete,static_file,response

def main():
    run(host='', port=8080)

def readme():
    response.content_type = 'text/plain; charset=UTF-8'
    return """
    
1. Readme
   curl http://localhost:8080/?readme

2. Listing
2.1. File Listing
   curl http://127.0.0.1:8080/

2.2. Read File
   curl http://127.0.0.1:8080/filename.txt

2.3. Download File
   curl http://127.0.0.1:8080/download/filename.txt

3. New File
3.1. Save Raw Text Data
   curl -X POST -d "This is a Test Upload" http://127.0.0.1:8080/testfile.txt
3.2. Upload A File
   curl -X POST --data-binary @add.py http://127.0.0.1:8080/testfile.txt

4. Edit A File
   curl -X PUT --data-binary "Overwritten Data"  http://127.0.0.1:8080/testfile.txt
   
5. Delete File
   curl -X DELETE http://127.0.0.1:8080/testfile.txt

    """
@get('/')
def read_dir():
    if 'readme' in request.GET:
        return readme() # /?readme
    import os
    listing=[]
    for subdir, dirs, files in os.walk('./'):
        for file in files:
           print file
           listing.append(file)
    return  {"listing": listing}

@post('/:filename')
@put('/:filename')
def create_a_file(filename):
    data = request.body.read()
    if not data:
        abort(400, 'No data received')
    file_extension = filename[filename.rfind('.')+1:].lower()
    print data
    #print file_extension
    oflags = 'w' if file_extension in ['txt','py','java','rb'] else 'wb'
    with open(filename, oflags) as f:
        f.write(data)
    return {"status":"ok"}

@get("/download/:filename")
def serve_download(filename):
    return static_file(filename, root='./', download=True) 

@get("/:filename")
def serve_view(filename):
    return static_file(filename, root='./', mimetype='text/plain')

@delete("/:filename")
def serve_delete(filename):
    import os
    #os.unlink(filename) # just to be safe for now :)
    return {"status":"ok"}
if __name__ == "__main__":
    main()
