import streamlit as st
import requests

# 페이지 설정
st.set_page_config(
    page_title="나만의 스마트 영어 단어장",
    page_icon="📚",
    layout="centered"
)

# 메인 타이틀 및 설명
st.title("📚 나만의 스마트 영어 단어장")
st.caption("영단어를 입력하면 한글 뜻, 영영 풀이, 발음, 품사, 유의어를 알려드립니다.")

# 검색창 입력
word_input = st.text_input("검색할 영어 단어를 입력하세요", placeholder="예: create, happy, apple")

if word_input.strip():
    word = word_input.strip().lower()
    
    with st.spinner("단어 정보를 검색하는 중입니다..."):
        # 1. Dictionary API (영영풀이, 발음, 품사, 유의어)
        dict_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        dict_response = requests.get(dict_url)
        
        # 2. MyMemory API (한글 번역)
        trans_url = f"https://api.mymemory.translated.net/get?q={word}&langpair=en|ko"
        trans_response = requests.get(trans_url)

    if dict_response.status_code == 200:
        dict_data = dict_response.json()[0]
        
        # 번역 결과 처리
        korean_meaning = "뜻을 가져올 수 없습니다."
        if trans_response.status_code == 200:
            trans_data = trans_response.json()
            if "responseData" in trans_data and trans_data["responseData"]["translatedText"]:
                korean_meaning = trans_data["responseData"]["translatedText"]

        st.markdown("---")
        
        # 단어 및 발음 표시
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header(dict_data.get('word', word))
            # 발음기호 찾기
            phonetic = dict_data.get('phonetic', '')
            if not phonetic and 'phonetics' in dict_data:
                for p in dict_data['phonetics']:
                    if 'text' in p and p['text']:
                        phonetic = p['text']
                        break
            if phonetic:
                st.subheader(f":blue[{phonetic}]")

        # 음성 오디오 찾기 (있을 경우 오디오 플레이어 출력)
        audio_url = None
        if 'phonetics' in dict_data:
            for p in dict_data['phonetics']:
                if p.get('audio'):
                    audio_url = p['audio']
                    break
        
        with col2:
            if audio_url:
                st.write("**발음 듣기**")
                st.audio(audio_url)

        # 🇰🇷 한글 뜻 박스
        st.success(f"**한글 뜻:** {korean_meaning}")

        # 📖 품사 및 영영 풀이 & 유의어 수집
        st.subheader("📖 품사 및 영영 풀이")
        all_synonyms = set()

        for meaning in dict_data.get('meanings', []):
            part = meaning.get('partOfSpeech', '기타')
            st.markdown(f"**[{part.upper()}]**")
            
            # 유의어 수집
            synonyms = meaning.get('synonyms', [])
            all_synonyms.update(synonyms)
            
            # 정의 출력 (최대 2개)
            for idx, def_info in enumerate(meaning.get('definitions', [])[:2], 1):
                st.write(f"{idx}. {def_info.get('definition')}")
                if def_info.get('example'):
                    st.caption(f"   *예문: {def_info.get('example')}*")
            st.write("")

        # 🔄 유의어 및 관련 품사 정보
        col_syn, col_der = st.columns(2)
        
        with col_syn:
            st.subheader("🔗 유의어")
            if all_synonyms:
                st.write(", ".join(list(all_synonyms)[:8]))
            else:
                st.caption("유의어 정보가 없습니다.")
                
        with col_der:
            st.subheader("🏷️ 등록된 품사")
            parts = [m.get('partOfSpeech') for m in dict_data.get('meanings', [])]
            st.write(", ".join(set(parts)))

    else:
        st.error("단어를 찾을 수 없습니다. 철자를 다시 확인해주세요!")
