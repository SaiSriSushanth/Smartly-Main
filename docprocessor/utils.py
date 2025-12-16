import os
import re
import json
import logging
from urllib.parse import quote, unquote, urlparse, parse_qs, urlencode
import urllib.request as urlrequest
from urllib.error import HTTPError, URLError
from django.conf import settings
from youtube_transcript_api import YouTubeTranscriptApi

# Initialize keys
OPENAI_KEY = getattr(settings, 'OPENAI_API_KEY', None) or os.environ.get('OPENAI_API_KEY')
ANTH_KEY = getattr(settings, 'ANTHROPIC_API_KEY', None) or os.environ.get('ANTHROPIC_API_KEY')
GOOGLE_KEY = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
HF_KEY = getattr(settings, 'HUGGINGFACE_API_KEY', None) or os.environ.get('HUGGINGFACE_API_KEY')

ALLOW_FALLBACKS = True

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyPDF2 (Lazy Loaded)."""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        return "Error: PyPDF2 not installed."
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_path):
    """Extract text from DOCX using python-docx (Lazy Loaded)."""
    try:
        import docx
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except ImportError:
        return "Error: python-docx not installed."
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

            if not openai_client:
                 return "OpenAI client not initialized."
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=final_messages,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return (response.choices[0].message.content or "") + "\n\n[model: gpt-3.5-turbo]"

    else:
        # Default OpenAI
        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)
        if not openai_client:
             return "OpenAI client not initialized."
        response = openai_client.chat.completions.create(
            model=model or "gpt-3.5-turbo",
            messages=final_messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        out = response.choices[0].message.content or ""
        out = _strip_think_blocks(out)
        return (out + f"\n\n[model: {model or 'gpt-3.5-turbo'}]")

def summarize_text(text, target_words=None, max_tokens=500, preset=None, model=None):
    """Summarize text using selected model/provider with optional preset formatting."""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        preset_instruction = ""
        if preset == 'bullet_points':
            preset_instruction = "Format strictly as a markdown bullet list. Use '-' at the start of each line. No introduction or conclusion. Keep bullets concise and study-friendly."
        elif preset == 'detailed_summary':
            preset_instruction = " Provide a comprehensive paragraph-style summary."
        elif preset == 'study_notes':
            preset_instruction = " Produce study notes: headings for topics, sub-bullets for key concepts and definitions."
        elif preset == 'brief_summary':
            preset_instruction = " Keep it brief for quick revision."
        messages = [
            {"role": "user", "content": f"Summarize the following text{word_instruction} and {preset_instruction} Avoid omitting key points.\n\n{text}"}
        ]
        return _route_chat(messages, system_prompt="You are a helpful assistant that summarizes text clearly and faithfully.", model=model or "gpt-3.5-turbo", max_tokens=max_tokens)
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def generate_answers(text, target_words=None, max_tokens=500, preset=None, model=None):
    """Generate answers using selected model/provider with optional preset type."""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        preset_instruction = ""
        if preset == 'exam_answers':
            preset_instruction = " Generate comprehensive, step-by-step exam answers. Use numbered steps and short headings for clarity."
        elif preset == 'practice_questions':
            preset_instruction = " Create 6-10 practice questions with detailed answers. Format as a numbered list where each item contains 'Q:' followed by the question and 'A:' followed by the answer."
        elif preset == 'study_plan':
            preset_instruction = " Draft a personalized study schedule. Use a bullet list grouped by days/weeks with time blocks and goals."
        messages = [
            {"role": "user", "content": f"Generate clear, step-by-step answers{word_instruction} to the following questions or content.{preset_instruction}\n\n{text}"}
        ]
        return _route_chat(messages, system_prompt="You are a helpful assistant that generates accurate, well-structured answers.", model=model or "gpt-3.5-turbo", max_tokens=max_tokens)
    except Exception as e:
        return f"Error generating answers: {str(e)}"

def analyze_text(text, target_words=None, max_tokens=500, preset=None, model=None):
    """Analyze text using selected model/provider with optional preset for analysis type."""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        preset_instruction = ""
        if preset == 'question_patterns':
            preset_instruction = " Identify recurring question patterns and topics. Output a bullet list. For each pattern, include a short label and 1-2 example phrasings."
        elif preset == 'predict_questions':
            preset_instruction = " Predict likely exam questions based on the content. Output as a numbered list of questions only, optionally include one-sentence rationale per item."
        elif preset == 'topic_importance':
            preset_instruction = " Rank topics by exam importance as a numbered list from most to least important, with a brief justification for each."
        messages = [
            {"role": "user", "content": f"Analyze the following text, identify key insights, and rank topics by importance{word_instruction}.{preset_instruction}\n\n{text}"}
        ]
        return _route_chat(messages, system_prompt="You are a helpful assistant that analyzes text and ranks topics by importance.", model=model or "gpt-3.5-turbo", max_tokens=max_tokens)
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

def translate_text(text, target_language, source_language='auto', max_tokens=500, model=None):
    """Translate text using selected model/provider."""
    try:
        messages = [
            {"role": "user", "content": f"Please translate the following text from {source_language} to {target_language}:\n\n{text}"}
        ]
        return _route_chat(messages, system_prompt="You are a helpful assistant that translates text.", model=model or "gpt-3.5-turbo", max_tokens=max_tokens)
    except Exception as e:
        return f"Error translating text: {str(e)}"

def translate_text_free(text, target_language_code, source_language_code='auto'):
    """Translate text using the free LibreTranslate API.
    - Tries multiple public endpoints for resilience.
    - Falls back to form-encoded POST if JSON fails.
    - Splits large inputs into chunks to avoid payload limits.
    - Does not require any API key.
    - target_language_code: e.g., 'es', 'fr', 'de', 'hi', 'en'.
    """
    endpoints = [
        'https://libretranslate.de/translate',
        'https://translate.argosopentech.com/translate',
        'https://translate.astian.org/translate',
        'https://libretranslate.com/translate',
    ]

    def _detect_language(sample_text):
        """Detect language using LibreTranslate /detect endpoint across fallbacks.
        Returns a language code or None if detection fails.
        """
        sample = (sample_text or '').strip()
        if not sample:
            return None
        sample = sample[:1000]
        detect_paths = [e.replace('/translate', '/detect') for e in endpoints]
        payload = {'q': sample}
        # Try JSON then form-encoded for each endpoint
        for endpoint in detect_paths:
            try:
                data_json = json.dumps(payload).encode('utf-8')
                req_json = urlrequest.Request(endpoint, data=data_json, headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'Smartly/1.0'})
                with urlrequest.urlopen(req_json, timeout=20) as resp:
                    body = resp.read().decode('utf-8')
                    parsed = json.loads(body)
                    # Expected: list of { language: 'en', confidence: 0.99 }
                    if isinstance(parsed, list) and parsed:
                        lang = parsed[0].get('language')
                        if lang:
                            return lang
            except Exception:
                pass
            try:
                data_form = urlencode(payload).encode('utf-8')
                req_form = urlrequest.Request(endpoint, data=data_form, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json', 'User-Agent': 'Smartly/1.0'})
                with urlrequest.urlopen(req_form, timeout=20) as resp:
                    body = resp.read().decode('utf-8')
                    parsed = json.loads(body)
                    if isinstance(parsed, list) and parsed:
                        lang = parsed[0].get('language')
                        if lang:
                            return lang
            except Exception:
                continue
        return None

    def _translate_chunk(chunk):
        chunk = chunk or ''
        if not chunk.strip():
            return ''
        # Determine source language if auto was requested
        src = source_language_code or 'auto'
        if (src == 'auto'):
            detected = _detect_language(chunk)
            if detected:
                src = detected
        payload = {
            'q': chunk,
            'source': src,
            'target': target_language_code,
            'format': 'text'
        }
        for endpoint in endpoints:
            # Try JSON first
            try:
                data_json = json.dumps(payload).encode('utf-8')
                req_json = urlrequest.Request(
                    endpoint,
                    data=data_json,
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'User-Agent': 'Smartly/1.0'
                    }
                )
                with urlrequest.urlopen(req_json, timeout=30) as resp:
                    body = resp.read().decode('utf-8')
                    parsed = json.loads(body)
                    translated = parsed.get('translatedText', '')
                    if translated and translated != chunk:
                        return translated
            except HTTPError as e:
                # Attempt to read error body to see if it contains JSON we can parse
                try:
                    err_body = e.read().decode('utf-8')
                    parsed_err = json.loads(err_body)
                    translated = parsed_err.get('translatedText', '')
                    if translated:
                        return translated
                except Exception:
                    pass
                # Fall through to form-encoded attempt
            except (URLError, Exception):
                # Fall through to form-encoded attempt
                pass

            # Form-encoded fallback
            try:
                data_form = urlencode(payload).encode('utf-8')
                req_form = urlrequest.Request(
                    endpoint,
                    data=data_form,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json',
                        'User-Agent': 'Smartly/1.0'
                    }
                )
                with urlrequest.urlopen(req_form, timeout=30) as resp:
                    body = resp.read().decode('utf-8')
                    parsed = json.loads(body)
                    translated = parsed.get('translatedText', '')
                    if translated and translated != chunk:
                        return translated
            except Exception:
                # Try next endpoint
                continue

        # Secondary fallback: MyMemory Translated API (free)
        try:
            def _mm_code(code: str) -> str:
                c = (code or '').lower()
                # Normalize Chinese variants
                if c in ('zh', 'zh-cn', 'cn', 'zh-hans'):
                    return 'zh-CN'
                if c in ('zh-tw', 'tw', 'zh-hant', 'zh-hk', 'hk'):
                    return 'zh-TW'
                # MyMemory does NOT support 'auto' or empty sources; default to English
                if not c or c in ('auto', 'und', 'unknown'):
                    return 'en'
                # Return as-is for typical 2-letter codes
                return code

            def _mm_translate_small(text_part: str) -> str:
                src_pair = f"{_mm_code(payload['source'])}|{_mm_code(payload['target'])}"
                query = urlencode({'q': text_part, 'langpair': src_pair})
                url = f"https://api.mymemory.translated.net/get?{query}"
                req_mm = urlrequest.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'Smartly/1.0'})
                    return mm_out
            else:
                out_parts = []
                start = 0
                while start < len(chunk):
                    end = min(start + mm_max, len(chunk))
                    newline_pos = chunk.rfind('\n', start, end)
                    space_pos = chunk.rfind(' ', start, end)
                    if newline_pos != -1 and newline_pos > start + 50:
                        end = newline_pos
                    elif space_pos != -1 and space_pos > start + 50:
                        end = space_pos
                    part = chunk[start:end]
                    translated_part = _mm_translate_small(part)
                    out_parts.append(translated_part or part)
                    start = end
                mm_joined = ''.join(out_parts)
                if mm_joined and mm_joined != chunk:
                    return mm_joined
        except Exception:
            pass

        # If none of the endpoints succeeded or translation unchanged
        return f"[Translation unchanged: provider unavailable or returned same text]"

    # Chunk by ~4000 characters to stay under typical API limits
    chunks = []
    max_len = 4000
    text = text or ''
    if len(text) <= max_len:
        chunks = [text]
    else:
        start = 0
        while start < len(text):
            end = min(start + max_len, len(text))
            # try to break at a newline for cleaner splits
            newline_pos = text.rfind('\n', start, end)
            if newline_pos != -1 and newline_pos > start + 1000:
                end = newline_pos
            chunks.append(text[start:end])
            start = end

    translated_parts = [_translate_chunk(c) for c in chunks]
    return ''.join(translated_parts)

def chat_with_openai(messages, system_prompt=None, model="gpt-3.5-turbo", max_tokens=800):
    """Generic chat helper using OpenAI ChatCompletion. Library uses this and must stay OpenAI."""
    try:
        import openai
        openai_client = None
        if OPENAI_KEY:
            openai_client = openai.OpenAI(api_key=OPENAI_KEY)
            
        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)
        if not openai_client:
             return "OpenAI client not initialized."
        response = openai_client.chat.completions.create(
            model=model,
            messages=final_messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return (response.choices[0].message.content or "") + f"\n\n[model: {model}]"
    except Exception as e:
        return f"Error chatting with OpenAI: {str(e)}\n\n[model: {model}]"


def recommend_youtube_videos_web(query, max_results=5, timeout=15, region=None):
    """Fetch current YouTube video recommendations using DuckDuckGo HTML search and YouTube oEmbed.
    - Returns a fenced smartly_videos JSON block for rich card rendering.
    - Filters out YouTube Shorts and deduplicates links.
    """
    try:
        q = f"site:youtube.com {query}".strip()
        ddg_url = "https://duckduckgo.com/html/?q=" + quote(q) + (f"&kl={quote(region)}" if region else "")
        req = urlrequest.Request(ddg_url, headers={'User-Agent': 'Smartly/1.0', 'Accept': 'text/html'})
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Error searching for videos: {str(e)}"

    # Extract result links from DuckDuckGo HTML (no-JS version)
    links = []
    try:
        for m in re.finditer(r'<a[^>]+class="[^\"]*result__a[^\"]*"[^>]+href="([^"]+)"', html, re.IGNORECASE):
            href = m.group(1)
            url = href
            if 'uddg=' in href:
                try:
                    parsed = urlparse(href)
                    qs = parse_qs(parsed.query)
                    if 'uddg' in qs and qs['uddg']:
                        url = unquote(qs['uddg'][0])
                    else:
                        mm = re.search(r'uddg=([^&]+)', href)
                        url = unquote(mm.group(1)) if mm else href
                except Exception:
                    url = href
            # Accept watch links and youtu.be; exclude shorts
            is_watch = ('youtube.com/watch' in url) or ('youtu.be/' in url)
            is_short = ('/shorts/' in url)
            if is_watch and not is_short:
                links.append(url)
            if len(links) >= max_results * 3:
                break
    except Exception:
        pass

    # Deduplicate while preserving order
    unique = []
    seen = set()
    for u in links:
        key = u.split('&')[0]
        if key not in seen:
            seen.add(key)
            unique.append(u)
        if len(unique) >= max_results * 2:
            break

    # Fetch title/channel via YouTube oEmbed (no API key) and build JSON
    results = []
    for link in unique:
        title = None
        channel = None
        thumb = None
        try:
            oembed = "https://www.youtube.com/oembed?format=json&url=" + quote(link, safe='')
            rq = urlrequest.Request(oembed, headers={'User-Agent': 'Smartly/1.0', 'Accept': 'application/json'})
            with urlrequest.urlopen(rq, timeout=timeout) as r2:
                data = json.loads(r2.read().decode('utf-8'))
                title = data.get('title')
                channel = data.get('author_name')
        except Exception:
            pass
        try:
            # Extract video id for thumbnail
            m = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})(?:[&?/]|$)', link)
            vid_id = m.group(1) if m else None
            if vid_id:
                thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
        except Exception:
            thumb = None
        results.append({'url': link, 'title': title or '', 'channel': channel or '', 'thumb': thumb or ''})

    if not results:
        return (
            "I couldn't find live YouTube links right now. Try refining the topic "
            "or check your network."
        )

    # Return structured fenced block for card rendering
    try:
        payload = json.dumps(results[:max_results])
        return f"```smartly_videos\n{payload}\n```"
    except Exception:
        # Fallback to markdown list
        lines = ["Here are current YouTube picks for your topic:", ""]
        for i, r in enumerate(results[:max_results], 1):
            t = r['title'] or f"Video {i}"
            ch = r['channel'] or 'YouTube'
            lines.append(f"- {t} — {ch}\n  {r['url']}")
        return "\n".join(lines)