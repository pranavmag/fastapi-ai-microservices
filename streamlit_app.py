import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="BrainDump", page_icon="🧠", layout="centered")

# ===== SESSION STATE =====
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# ===== API HELPERS =====
def login(username, password):
    r = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    return r

def register(username, email, password):
    r = requests.post(f"{API_URL}/register", json={"username": username, "email": email, "password": password})
    return r

def get_notes():
    r = requests.get(f"{API_URL}/notes", headers=auth_headers())
    return r.json() if r.status_code == 200 else []

def create_note(content, tags):
    r = requests.post(f"{API_URL}/notes", headers=auth_headers(),
                      json={"content": content, "tags": tags, "is_completed": False})
    return r

def delete_note(note_id):
    r = requests.delete(f"{API_URL}/notes/{note_id}", headers=auth_headers())
    return r

def toggle_complete(note, completed):
    r = requests.put(f"{API_URL}/notes/{note['id']}", headers=auth_headers(),
                     json={"content": note["content"], "tags": note.get("tags"), "is_completed": completed})
    return r

# ===== AUTH PAGE =====
def show_auth_page():
    st.title("🧠 BrainDump")
    st.caption("AI-powered notes app")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                r = login(username, password)
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register", use_container_width=True)
            if submitted:
                r = register(new_username, email, new_password)
                if r.status_code == 201:
                    st.success("Account created! Please log in.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))

# ===== NOTES PAGE =====
def show_notes_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🧠 BrainDump")
        st.caption(f"Logged in as **{st.session_state.username}**")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()

    with st.expander("➕ New Note", expanded=False):
        with st.form(f"create_note_form_{st.session_state.form_key}"):
            content = st.text_area("Note content", height=100, placeholder="What's on your mind?")
            tags = st.text_input("Tags (optional)", placeholder="work, ideas, personal")
            submitted = st.form_submit_button("Create Note", use_container_width=True)
            if submitted:
                if content.strip():
                    r = create_note(content, tags if tags else None)
                    if r.status_code == 201:
                        st.session_state.form_key += 1
                        st.success("Note created!")
                        st.rerun()
                    else:
                        st.error("Failed to create note")
                else:
                    st.warning("Note content cannot be empty")

    st.divider()

    notes = get_notes()

    if not notes:
        st.info("No notes yet. Create your first note above!")
        return

    st.subheader(f"Your Notes ({len(notes)})")

    for note in reversed(notes):
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                if note.get("tags"):
                    tags_list = [f"`{t.strip()}`" for t in note["tags"].split(",")]
                    st.markdown(" ".join(tags_list))

                if note.get("is_completed"):
                    st.markdown(f"~~{note['content']}~~")
                else:
                    st.write(note["content"])

                if note.get("ai_summary"):
                    st.info(f"🤖 **AI Summary:** {note['ai_summary']}")

                created = note["created_at"][:10]
                st.caption(f"Created: {created}")

            with col2:
                is_done = note.get("is_completed", False)
                label = "✅ Done" if is_done else "⬜ Complete"
                if st.button(label, key=f"complete_{note['id']}", use_container_width=True):
                    toggle_complete(note, not is_done)
                    st.rerun()

                if st.button("🗑️ Delete", key=f"delete_{note['id']}", use_container_width=True):
                    delete_note(note["id"])
                    st.rerun()

# ===== MAIN =====
if st.session_state.token:
    show_notes_page()
else:
    show_auth_page()
