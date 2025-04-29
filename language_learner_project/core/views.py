import json
import logging
import os
import re
from datetime import datetime, timezone

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CourseForm, ModuleForm, SentenceForm
from .models import Course, Module, Sentence, UserModule, Word
from .utils import split_into_sentences

logger = logging.getLogger(__name__)


@login_required
def create_course_modal(request):
    form = CourseForm()
    html = render_to_string(
        "courses/_course_form.html", {"form": form}, request=request
    )
    return HttpResponse(html)


@login_required
def create_course_submit(request):
    form = CourseForm(request.POST)
    if form.is_valid():
        course = form.save(commit=False)
        course.creator = request.user
        course.save()
        course.members.add(request.user)
        return HttpResponse("<script>location.reload()</script>")
    else:
        html = render_to_string(
            "courses/_course_form.html", {"form": form}, request=request
        )
        return HttpResponse(html, status=400)


@login_required
def explore_courses(request):
    available_courses = (
        Course.objects.filter(is_public=True)
        .exclude(creator=request.user)
        .exclude(members=request.user)
    )

    return render(request, "courses/explore.html", {"courses": available_courses})


@login_required
def join_course(request, pk):
    course = get_object_or_404(Course, pk=pk, is_public=True)
    if course.creator != request.user and request.user not in course.members.all():
        course.members.add(request.user)
    return redirect("explore_courses")


# Create your views here.
def home(request):
    return render(request, "home.html")


def time_partial(request):
    return render(request, "partials/time.html", {"now": datetime.now()})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    modules = course.modules.all().order_by('order')
    module_data = []

    for module in modules:
        usermodule = module.usermodules.filter(user=request.user).first()
        module_data.append(
            {
                "module": module,
                "usermodule": usermodule,
            }
        )

    user_modules = UserModule.objects.filter(user=request.user, module__in=modules)
    started_modules = user_modules.filter(started_at__isnull=False).count()
    completed_modules = user_modules.filter(completed_at__isnull=False).count()
    total_modules = modules.count()

    if total_modules > 0:
        # 🛠 Här räknar vi poäng för påbörjade + klara
        progress = (started_modules / total_modules) * 50 + (
            completed_modules / total_modules
        ) * 50
    else:
        progress = 0

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "module_data": module_data,
            "progress": progress,
        },
    )


@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = CourseForm(instance=course)

    return render(request, "courses/course_edit.html", {"form": form, "course": course})


@login_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.creator = request.user
            course.save()
            course.members.add(request.user)  # Gör skaparen till medlem
            return redirect("profile")
    else:
        form = CourseForm()

    return render(request, "courses/course_create.html", {"form": form})


@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = CourseForm(instance=course)

    members = course.members.all()

    return render(
        request,
        "courses/course_edit.html",
        {
            "form": form,
            "course": course,
            "members": members,
        },
    )


@login_required
def edit_course_modules(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)
    modules = course.modules.order_by('order')
    return render(
        request,
        "courses/course_edit_modules.html",
        {"course": course, "modules": modules},
    )


@login_required
def module_create(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)
    if request.method == "POST":
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)

            # Efter form.save()
            module = form.save(commit=False)
            module.course = course

            # Sanera excluded_words
            if module.excluded_words:
                words = [
                    w.strip().lower()
                    for w in module.excluded_words.split(",")
                    if w.strip()
                ]
                module.excluded_words = ", ".join(sorted(set(words)))

            module.save()
            return HttpResponse("<script>location.reload()</script>")
    else:
        form = ModuleForm()
    html = render_to_string(
        "courses/_module_form.html", {"form": form, "course": course}, request=request
    )  # 🛠 Lägg till course här!
    return HttpResponse(html)


@login_required
def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk, course__creator=request.user)
    if request.method == "POST":
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            # Efter form.save()
            module = form.save(commit=False)

            # Sanera excluded_words
            if module.excluded_words:
                words = [
                    w.strip().lower()
                    for w in module.excluded_words.split(",")
                    if w.strip()
                ]
                module.excluded_words = ", ".join(sorted(set(words)))

            module.save()

            return HttpResponse("<script>location.reload()</script>")
    else:
        form = ModuleForm(instance=module)
        html = render_to_string(
            "courses/_module_form.html",
            {"form": form, "course": module.course},  #  Skicka in course!
            request=request,
        )
    return HttpResponse(html)


@csrf_exempt
@login_required
def module_reorder(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)
    data = json.loads(request.body)
    order = data.get('order', [])
    for index, module_id in enumerate(order):
        Module.objects.filter(pk=module_id, course=course).update(order=index)
    return HttpResponse("OK")


@login_required
@require_POST
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)

    if module.course.creator != request.user:
        return HttpResponse(status=403)

    module.delete()

    logger.info(f"Module {pk} deleted by user {request.user.id}")

    return HttpResponse(status=204)


# core/views.py
from core.utils import split_into_sentences  # vi använder den!


def extract_clean_words(text):
    """
    Tar ut rena ord från text: små bokstäver, utan skiljetecken.
    """
    cleaned_text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    words = cleaned_text.lower().split()
    return words


@login_required
@require_POST
def generate_sentences(request, pk):
    """
    Skapar meningar och unika ord från en moduls text.
    Tar hänsyn till exkludering och kursens befintliga ord.
    """
    module = get_object_or_404(Module, pk=pk, course__creator=request.user)

    # Radera tidigare meningar och ord från modulen
    module.sentences.all().delete()
    module.words.all().delete()

    # 🧠 Dela upp text i meningar
    sentences = split_into_sentences(module.text, module.course.language)

    for index, text in enumerate(sentences):
        Sentence.objects.create(module=module, text=text.strip(), order=index)

    # 🛡️ Hämta befintliga ord i hela kursen
    all_excluded_words = set(
        Word.objects.filter(module__course=module.course).values_list('text', flat=True)
    )

    # 🛡️ Lägg till ord från modulens egna exclude-lista
    if module.excluded_words:
        manual_excludes = [
            w.strip().lower() for w in module.excluded_words.split(',') if w.strip()
        ]
        all_excluded_words.update(manual_excludes)

    # 🪄 Extrahera nya ord från texten
    words_in_text = extract_clean_words(module.text)

    # Koppla ord till första mening där de förekommer
    for word in words_in_text:
        word_clean = word.strip().lower()
        if word_clean and word_clean not in all_excluded_words:
            example_sentence = None
            for s in sentences:
                if word_clean in s.lower():
                    example_sentence = Sentence.objects.filter(
                        module=module, text__icontains=s.strip()
                    ).first()
                    break

            Word.objects.create(
                module=module, text=word.strip(), example_sentence=example_sentence
            )
            all_excluded_words.add(word_clean)

    # 🔄 Rendera om hela modalsidan
    html = render_to_string(
        "courses/_module_form.html",
        {"form": ModuleForm(instance=module), "course": module.course},
        request=request,
    )

    return HttpResponse(html)


@login_required
def sentence_edit(request, pk):
    sentence = get_object_or_404(Sentence, pk=pk, module__course__creator=request.user)

    if request.method == "POST":
        form = SentenceForm(request.POST, instance=sentence)
        if form.is_valid():
            form.save()
            return HttpResponse("<script>location.reload()</script>")
    else:
        form = SentenceForm(instance=sentence)

    html = render_to_string(
        "courses/_sentence_form.html", {"form": form}, request=request
    )
    return HttpResponse(html)


def extract_unique_words(text):
    # Enkelt tokenizer (du kan förbättra senare)
    words = re.findall(r'\b\w+\b', text.lower())
    return sorted(set(words))  # unika och sorterade


@require_POST
@login_required
def regenerate_sentences(request, pk):
    module = get_object_or_404(Module, pk=pk, course__creator=request.user)

    # Rensa tidigare
    module.sentences.all().delete()
    module.words.all().delete()

    # Skapa meningar
    sentences = split_into_sentences(module.text, module.course.language)
    logger.info(f"Antal meningar skapade: {len(sentences)}")

    for idx, text in enumerate(sentences):
        Sentence.objects.create(module=module, text=text.strip(), order=idx)

    # Ord från andra moduler
    existing_words = set(
        Word.objects.filter(module__course=module.course)
        .exclude(module=module)
        .values_list('text', flat=True)
    )
    logger.info(f"Existerande ord i kursen: {existing_words}")

    # Stopplista
    extra_excluded = set(
        word.strip().lower()
        for word in module.excluded_words.split(",")
        if word.strip()
    )
    logger.info(f"Extra exkluderade ord: {extra_excluded}")

    # Extrahera råa ord
    raw_words = extract_words_from_text(module.text)
    logger.info(f"Extraherade ord: {raw_words}")

    # Skapa ord
    created_words = set()
    for word in raw_words:
        cleaned_word = word.lower().strip()
        if (
            len(cleaned_word) >= 2
            and cleaned_word not in existing_words
            and cleaned_word not in extra_excluded
            and cleaned_word not in created_words
        ):
            Word.objects.create(module=module, text=cleaned_word)
            created_words.add(cleaned_word)

    logger.info(f"Antal ord skapade: {len(created_words)}")

    return HttpResponse(status=204)


@login_required
@require_POST
def regenerate_sentences(request, pk):
    module = get_object_or_404(Module, pk=pk, course__creator=request.user)

    # 🛑 Ta bort gamla meningar
    module.sentences.all().delete()

    # ➡️ Skapa nya
    from .utils import split_into_sentences

    sentences = split_into_sentences(module.text, module.course.language)
    for order, sentence_text in enumerate(sentences):
        Sentence.objects.create(module=module, text=sentence_text, order=order)

    return HttpResponse(status=204)  # 204 = No Content, snabb och snygg!


@login_required
@require_http_methods(["POST"])
def sentence_inline_edit(request, pk):
    sentence = get_object_or_404(Sentence, pk=pk, module__course__creator=request.user)
    data = json.loads(request.body)

    field = data.get("field")
    value = data.get("value")

    if field in ["text", "translation"]:
        setattr(sentence, field, value)
        sentence.save()
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)


# --- Ladda upp ljudfil ---
@login_required
@require_http_methods(["POST"])
def sentence_upload_audio(request, pk):
    sentence = get_object_or_404(Sentence, pk=pk, module__course__creator=request.user)
    if 'audio' in request.FILES:
        sentence.audio = request.FILES['audio']
        sentence.save()
        html = render_to_string(
            "courses/_sentence_card.html", {"sentence": sentence}, request=request
        )
        return HttpResponse(html)
    return JsonResponse({"error": "Ingen fil mottagen."}, status=400)


# --- Radera ljudfil ---
@login_required
@require_http_methods(["POST"])
def sentence_delete_audio(request, pk):
    sentence = get_object_or_404(Sentence, pk=pk, module__course__creator=request.user)
    if sentence.audio:
        sentence.audio.delete(save=True)
    return JsonResponse({"success": True})


@csrf_exempt
@login_required
@require_POST
def edit_word_translation(request, pk):
    """Uppdatera en översättning för ett Word-objekt"""
    word = get_object_or_404(Word, pk=pk, module__course__creator=request.user)
    data = json.loads(request.body)
    word.translation = data.get("translation", "")
    word.save()
    return JsonResponse({"status": "success"})


@csrf_exempt
@login_required
@require_POST
def upload_word_image(request, pk):
    """Ladda upp bild till ett Word-objekt"""
    word = get_object_or_404(Word, pk=pk, module__course__creator=request.user)
    word.image = request.FILES.get("image")
    word.save()
    return JsonResponse({"status": "success"})


@csrf_exempt
@login_required
@require_POST
def upload_word_audio(request, pk):
    """
    Ladda upp ljud till ett Word-objekt på ett säkert sätt.
    """
    word = get_object_or_404(Word, pk=pk, module__course__creator=request.user)

    audio_file = request.FILES.get("audio")
    if not audio_file:
        return JsonResponse({"error": "Ingen ljudfil mottagen."}, status=400)

    word.audio = audio_file
    word.save()

    return JsonResponse({"status": "success", "audio_url": word.audio.url})


@require_POST
@login_required
def sentence_delete_audio(request, pk):
    sentence = get_object_or_404(Sentence, pk=pk, module__course__creator=request.user)
    if sentence.audio:
        audio_path = sentence.audio.path
        if os.path.exists(audio_path):
            os.remove(audio_path)
        sentence.audio = None
        sentence.save()
    html = render_to_string(
        "courses/_sentence_card.html", {"sentence": sentence}, request=request
    )
    return HttpResponse(html)


@require_POST
@login_required
def word_delete_audio(request, pk):
    word = get_object_or_404(Word, pk=pk, module__course__creator=request.user)
    if word.audio:
        audio_path = word.audio.path
        if os.path.exists(audio_path):
            os.remove(audio_path)
        word.audio = None
        word.save()
    return JsonResponse({"status": "success"})


@login_required
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    usermodule = module.usermodules.filter(user=request.user).first()

    # Exportera meningar som JSON
    sentences = module.sentences.all()
    sentences_json = json.dumps(
        [
            {
                "id": s.id,
                "text": s.text,
                "translation": s.translation,
                "audio": s.audio.url if s.audio else None,
            }
            for s in sentences
        ]
    )

    # Exportera ord som JSON
    words = module.words.all()
    words_json = json.dumps(
        [
            {
                "id": w.id,
                "text": w.text,
                "translation": w.translation,
                "image": w.image.url if w.image else None,
                "audio": w.audio.url if w.audio else None,
            }
            for w in words
        ]
    )

    # Bygg Cloze-data
    cloze_data = []
    for sentence in sentences:
        if sentence.text:
            words_in_sentence = sentence.text.split()
            for word in words_in_sentence:
                clean_word = word.strip('.,!?').lower()
                # Bara skapa lucktext om ordet finns i wordlistan!
                if module.words.filter(text__iexact=clean_word).exists():
                    cloze_text = sentence.text.replace(word, "[___]", 1)
                    cloze_data.append(
                        {
                            "cloze": cloze_text,
                            "missingWord": clean_word,
                            "translation": sentence.translation or "",
                            "audio": sentence.audio.url if sentence.audio else None,
                        }
                    )

    cloze_json = json.dumps(cloze_data)

    return render(
        request,
        "courses/module_detail.html",
        {
            "module": module,
            "usermodule": usermodule,
            "sentences_json": sentences_json,
            "words_json": words_json,
            "cloze_json": cloze_json,
        },
    )


@login_required
@require_POST
def complete_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    user_module, created = UserModule.objects.get_or_create(
        user=request.user, module=module
    )

    user_module.completed = True
    user_module.save()

    # 🔥 Hitta nästa modul
    next_module = (
        Module.objects.filter(course=module.course, order__gt=module.order)
        .order_by('order')
        .first()
    )

    if next_module:
        # 🔥 Skapa UserModule för nästa modul om det inte finns
        UserModule.objects.get_or_create(user=request.user, module=next_module)
    else:
        # 🏆 Om ingen nästa modul → hela kursen klar!
        messages.success(request, "Grattis! Du har klarat hela kursen! 🎉")

    return redirect("course_detail", pk=module.course.pk)


@login_required
@require_POST
def start_module(request, pk):
    module = get_object_or_404(Module, pk=pk)

    usermodule, created = UserModule.objects.get_or_create(
        user=request.user,
        module=module,
    )
    if created:
        usermodule.started_at = timezone.now()
        usermodule.save()

    return redirect('module_detail', pk=module.pk)


@login_required
@require_POST
def complete_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    usermodule = module.usermodules.filter(user=request.user).first()
    if usermodule:
        usermodule.completed = True
        usermodule.save()
    return redirect("course_detail", pk=module.course.pk)


@login_required
@require_POST
def module_complete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    usermodule = UserModule.objects.filter(user=request.user, module=module).first()

    if usermodule:
        usermodule.completed_at = now()  # 🛠 Sätt när eleven klarat modulen
        usermodule.save()

        # --- Lås upp nästa modul om det finns
        next_module = (
            Module.objects.filter(course=module.course, order__gt=module.order)
            .order_by('order')
            .first()
        )
        if next_module:
            UserModule.objects.get_or_create(user=request.user, module=next_module)

    return redirect('course_detail', pk=module.course.pk)
