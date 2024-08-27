from datetime import datetime
from flask import Blueprint, render_template, request, flash , redirect , url_for  , send_file , render_template_string
from flask_login import login_required, current_user
from .file_manager import  FileManager
from .job_system import jobSystem
from .user_system import userSystem
from .application_system import applicationsSystem
from .submission_system import submissionSystem
from .models import Job


job_views = Blueprint('job_views', __name__)

@job_views.route('/browse-jobs' , methods = ['GET' , 'POST'] )
@login_required
def browse_jobs():
    jobs = jobSystem.GetAllJobs()
    return render_template("Jobs/browse_jobs.html" ,user=current_user ,jobs = jobs )


@job_views.route('/jobs/<int:job_id>/apply', methods=['POST' ,'GET'])
@login_required
def apply_job(job_id):
    if current_user.usertype == 'Business Owner' :
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404
    if jobSystem.ApplyForJob(job_id, current_user.id):
        flash('You have applied to this job!', 'success')
    else :
        flash('Something went wrong!', 'error')
    print(f"Applied to job with id {job_id}")
    return redirect(request.referrer)

@job_views.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    
    if current_user.usertype == 'Freelancer' :
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404
    if request.method == 'POST':
        job_name = request.form['job_name']
        job_description = request.form['job_description']
        job_details = request.form['details']
        job_payment = request.form['job_payment']
        job_deadline = request.form['job_deadline']
        file = request.files['img']
        print(file)
        job_deadline = datetime.strptime(job_deadline, '%Y-%m-%d' )
        if file.filename :
            if not FileManager.IsImage(file) :
                flash('Invalid file type', 'error')
                return render_template('Jobs/post_job.html' ,user = current_user)
        else :
            file = None
        job = Job(job_name=job_name, job_description=job_description,  job_details = job_details,job_payment=job_payment,  job_deadline=job_deadline, user=current_user)
        if  jobSystem.PostJob(job , file):
            flash('Your job has been posted!', 'success')
            return redirect(url_for('job_views.browse_jobs'))
        else : 
            flash('Something went wrong!', 'error')
            return render_template('Jobs/post_job.html' ,user = current_user)
           
    return render_template('Jobs/post_job.html' ,user = current_user)

@job_views.route('/jobs/<int:job_id>/expand', methods=['GET' , 'POST'])
@login_required
def expand_job(job_id):
    job = jobSystem.GetJob(job_id)
    img = get_job_image(job_id)

    applications_list = []
    if job.user_id == current_user.id :
        applications = jobSystem.GetJobApplications(job_id) 
        print(applications)
        applications_list = []
        for application in applications :
            applications_list.append((application , userSystem.GetUser(application.user_id )))  
    print("job" , job.user_id)
    print(current_user.id)
    print(applications_list)
    return render_template('Jobs/job_expanded.html', job=job, user=current_user , img = img , applications = applications_list)


@job_views.route('/jobs/<int:job_id>/get-image', methods=['GET'])
@login_required
def get_job_image(job_id):
    job_img = jobSystem.GetJobImage(job_id)
    
    if job_img :
        print(job_img.image_path)
        return send_file('../' + job_img.image_path, mimetype='image/jpg')
    else :
        return None


@job_views.route('/jobs/posted-by-user', methods=['GET'])
@login_required
def get_jobs_posted_by_user():  
    if current_user.usertype == 'Freelancer' :
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404

    jobs = jobSystem.GetPostedJobs(current_user.id)
    return render_template('Jobs/posted_jobs.html' ,user=current_user ,jobs = jobs )

@job_views.route('/jobs/delete/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    jobSystem.DeleteJob(job_id , current_user.id)
    return redirect(request.referrer)

@job_views.route('/jobs/applications/my-applications', methods=['GET' , 'POST'])
@login_required
def get_user_applications():
    applications = applicationsSystem.GetApplicationsByUser(current_user.id)
    return render_template('my_applications.html' , user = current_user , applications = applications)


@job_views.route('jobs/applications/<int:application_id>/reject', methods=['POST'])
@login_required
def reject_application(application_id):
    applicationsSystem.RejectApplication(application_id)
    return redirect(request.referrer)

@job_views.route('jobs/applications/<int:application_id>/accept', methods=['POST'])
@login_required 
def accept_application(application_id): 
    applicationsSystem.AcceptApplication(application_id)
    return redirect(request.referrer)



@job_views.route('jobs/submission/make-submission/<int:application_id>', methods = ['GET' , 'POST'])
@login_required
def make_submission(application_id : int) :
    if current_user == 'Buisness Owner' :
        return render_template_string('PageNotFound ', errorCode='404'), 404

    print(request.method)
    app = applicationsSystem.GetApplicationById(application_id)
    if request.method == 'POST' :
        file = request.files['file']
        title = request.form['submission_title']
        if submissionSystem.MakeSubmission(application_id , file= file , title= title):
            flash('Submission made successfully', 'success')
            return redirect(request.referrer)
        
        flash('Invalid submission', 'error')
        return redirect(request.referrer)
    return render_template('jobs/make_submission.html' , user = current_user ,app = app )

@job_views.route('jobs/aplications/my_applications')
@login_required
def get_applications() :
    applications = applicationsSystem.GetApplicationsByUser(current_user.id)
    return render_template('my_applications.html' , user = current_user , applications = applications)


@job_views.route('jobs/submission/recv_submissions' , methods = ['GET'])
@login_required
def recv_submissions() :
    if current_user.usertype == 'Freelancer' :
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404
    submissions = submissionSystem.GetSubmissionsToUser(current_user.id)
    return render_template('jobs/recv_submissions.html' , user = current_user , submissions = submissions)

@job_views.route('jobs/submission/accept_submission/<int:submission_id>', methods = ['POST'])
@login_required
def accept_submission(submission_id : int) :
    print(submission_id)
    if current_user.usertype == 'Freelancer'  :
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404
    if submissionSystem.AcceptSubmission(submission_id , current_user) :
        flash("Accepted submission" , "success")
    else :
        flash("Error accepting submission" , "error")
    return redirect(request.referrer)


@job_views.route('/jobs/submissions/download-file/<int:submission_id>', methods=['GET'])
@login_required
def download_file(submission_id):
    print(submission_id)
    if current_user.usertype == 'Freelancer' :
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404
    submission:submissionSystem = submissionSystem.GetSubmissionById(submission_id)
    if submission.application.job.user_id != current_user.id :
        return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404
    return send_file('../' + submission.file_path,as_attachment=True)