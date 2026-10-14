# Digital Electronics K-Map Solver

**Student:** Amit Kumar Patra  
**Registration:** 2501020717  
**College:** C. V. Raman Global University  
**Department:** Electronics and Communication Engineering (ECE)

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start the app:
   `streamlit run app.py`
5. Open the local URL printed by Streamlit (usually `http://localhost:8501`).

## Deploy to a public website
1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Sign in to Streamlit Community Cloud and choose **Create app**.
3. Select your repository, branch, and `app.py` as the main file.
4. Deploy; copy the public app URL after deployment finishes.

The app supports 2-, 3-, and 4-variable K-maps, standard Gray-code order, minterm/maxterm inputs, optional don't-care terms, SOP/POS minimization, a step-by-step learning summary, and downloadable text reports.

Note: the step-by-step section explains the minimization workflow; it does not claim to display exact individual grouping overlays on the map.
