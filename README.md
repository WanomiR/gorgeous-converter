# Gorgeous Converter
The best raw photo converter you have ever known.


### App instructions
App installation instructions for Mac with M1.
1. Download the project files.
    ```bash
   git clone https://github.com/WanomiR/gorgeous-converter
   ```
2. Open the project's root directory and create a virtual environment.
   ```bash
   python3.10 -m venv venv
   ```
3. Activate the environment, upgrade `pip`, and install dependencies.
   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   ```
4. Install rawpy from the source.
    ```bash
    brew install libraw cmake llvm
    sudo ln -s /opt/homebrew/opt/libomp/lib/libomp.dylib libomp.dylib

    git clone https://github.com/letmaik/rawpy
    cd rawpy
    pip install wheel numpy cython
    pip install .
    ```
5. Remove rawpy directory after installation is finished.
    ```bash
   cd ../ && rm -rf rawpy/
   ```
6. Return to the project's root directory and install other project rquirements.
    ```bash
    pip install -r requirements.txt
    ```

7. Open the `src` directory and run the main script with Streamlit.
   ```bash
   cd src && streamlit run app.py
   ```
