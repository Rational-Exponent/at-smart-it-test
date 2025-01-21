import streamlit as st


def main():
    # Initialize the page
    st.header("Caution: Experimental AI ahead!")

    query = st.text_input("What is your query?")
    if query:
        st.session_state.queries.append(query)
    
    if st.session_state.queries:
        for idx, q in enumerate(st.session_state.queries):
            st.write(f"{idx + 1}. {q}")


if __name__ == "__main__":
    if 'queries' not in st.session_state:
        st.session_state.queries = []
    main()