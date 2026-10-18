import glob
import os
import shutil

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from services.preprocessing.data_cleaner import DataError
from services.recommendation import recommendation_engine as engine

upload_bp = Blueprint("upload", __name__)


def user_file(user_id):
    """Path of the user's current workbook, or None."""
    d = os.path.join(current_app.config["UPLOAD_FOLDER"], f"user_{user_id}")
    hits = glob.glob(os.path.join(d, "data.*"))
    return hits[0] if hits else None


def _save(user_id, src_stream_or_path, ext, display_name="data"):
    d = os.path.join(current_app.config["UPLOAD_FOLDER"], f"user_{user_id}")
    os.makedirs(d, exist_ok=True)
    for old in glob.glob(os.path.join(d, "data.*")):
        os.remove(old)
    dest = os.path.join(d, f"data.{ext}")
    with open(os.path.join(d, "name.txt"), "w", encoding="utf-8") as fh:
        fh.write(os.path.basename(display_name))
    if isinstance(src_stream_or_path, str):
        shutil.copy(src_stream_or_path, dest)
    else:
        src_stream_or_path.save(dest)
    return dest


def original_name(user_id, default="data"):
    p = os.path.join(current_app.config["UPLOAD_FOLDER"], f"user_{user_id}", "name.txt")
    try:
        with open(p, encoding="utf-8") as fh:
            return fh.read().strip() or default
    except OSError:
        return default


@upload_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if request.form.get("use_sample"):
            name = "WideLens_Nagpur_Sample.xlsx"
            dest = _save(current_user.id, current_app.config["SAMPLE_FILE"], "xlsx", name)
        else:
            f = request.files.get("file")
            if not f or not f.filename:
                flash("Choose an Excel (.xlsx) or CSV file first.", "danger")
                return redirect(url_for("upload.upload"))
            ext = f.filename.rsplit(".", 1)[-1].lower()
            if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
                flash("Unsupported file type. Upload .xlsx or .csv.", "danger")
                return redirect(url_for("upload.upload"))
            name = f.filename
            dest = _save(current_user.id, f, ext, name)
        try:
            engine.load(dest)          # validate + analyse now so errors show here
        except DataError as e:
            os.remove(dest)
            flash(str(e), "danger")
            return redirect(url_for("upload.upload"))
        except Exception as e:  # noqa: BLE001
            current_app.logger.exception("analysis failed")
            os.remove(dest)
            flash(f"Could not analyse that file ({type(e).__name__}). Check it matches the template.", "danger")
            return redirect(url_for("upload.upload"))
        flash(f"Analysed {name}.", "success")
        return redirect(url_for("dash.index"))
    return render_template("upload.html", has_data=bool(user_file(current_user.id)))


@upload_bp.route("/sample.xlsx")
def sample_download():
    return send_file(current_app.config["SAMPLE_FILE"], as_attachment=True, download_name="WideLens_Nagpur_Sample.xlsx")
