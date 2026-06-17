from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, Question, Choice, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    questions = Question.objects.filter(course=course)
    return render(request, 'onlinecourse/course_details_bootstrap.html', {
        'course': course,
        'questions': questions,
    })


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )

        submission = Submission.objects.create(enrollment=enrollment)

        selected_choices = request.POST.getlist('choice')
        for choice_id in selected_choices:
            choice = get_object_or_404(Choice, pk=choice_id)
            submission.choices.add(choice)

        return redirect(
            'onlinecourse:show_exam_result',
            course_id=course.id,
            submission_id=submission.id
        )

    return redirect('onlinecourse:course_details', course_id=course.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_choices = submission.choices.all()
    questions = Question.objects.filter(course=course)

    total_score = 0
    full_score = 0

    for question in questions:
        full_score += question.grade
        correct_choices = question.choice_set.filter(is_correct=True)
        selected_for_question = selected_choices.filter(question=question)

        if set(correct_choices) == set(selected_for_question):
            total_score += question.grade

    passed = total_score >= full_score * 0.8 if full_score > 0 else False

    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'course': course,
        'submission': submission,
        'selected_choices': selected_choices,
        'total_score': total_score,
        'full_score': full_score,
        'passed': passed,
    })
