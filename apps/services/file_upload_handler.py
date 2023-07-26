import os, logging
from flask import make_response
from flask.wrappers import Request, Response
from werkzeug.utils import secure_filename


def handle_file_uploads(request: Request) -> Response:
    file_data = request.files["citadel_file_upload_dropper"]
    # save_path = os.path.join(config.data_dir, secure_filename(file_data.filename))

    save_path = os.path.join(
        "/Users/virwali/Main-area-for-backups/viresh/my_work/Aark-Global/Citadel-IDP/vscode-all/Adminlte3-flask/uploaded_file_storage",
        secure_filename(file_data.filename),
    )

    current_chunk = int(request.form["dzchunkindex"])
    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return make_response(("File already exists.", 400))
    try:
        with open(save_path, "ab") as f:
            f.seek(int(request.form["dzchunkbyteoffset"]))
            f.write(file_data.stream.read())
    except OSError:
        # log.exception will include the traceback so we can see what's wrong
        logging.exception("Could not write to file")
        return make_response(("Not sure why, but we couldn't write the file to disk", 500))

    total_chunks = int(request.form["dztotalchunkcount"])
    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form["dztotalfilesize"]):
            logging.error(
                "File %s was completed, but has a size mismatch. Was %s but we expected %s",
                file_data.filename,
                os.path.getsize(save_path),
                request.form["dztotalfilesize"],
            )

            return make_response(("Size mismatch", 500))
        else:
            logging.info("File %s has been uploaded successfully.", file_data.filename)
    else:
        logging.info("Chunk %s of %s for file %s complete", current_chunk + 1, total_chunks, file_data.filename)

    return make_response(("Chunk upload successful", 200))
