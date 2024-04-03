const authenticateBtn = document.getElementById('authenticateBtn');
const btnText = authenticateBtn.innerText;
const currentUrl = window.location.href;
const params = new URLSearchParams(window.location.search);
const token = params.get('token');
const id = params.get('id');
const apiUrl = "http://localhost:5000/api/";

if (!window.PublicKeyCredential) {
    showToast("Error: Cliente no compatible, por favor prueba con otro browser o dispositivo");
}

validateLink().then(response => {
    if (!response.isValid) {
        showToast("Error: link invalido, solicita uno nuevo y asegurate de usar el ultimo recibido");
        return;
    }
    addListeners(response);
    authenticateBtn.disabled = false;
}).catch(error => {
    showToast("Error en la conexion con el servidor, por favor intenta de nuevo mas tarde.");
    console.error(error)
});

function addListeners(response) {
    authenticateBtn.addEventListener('click', async () => {
        startSpinner();
        const createNew = response.createNewCredential;
        const credentialOptions = formatCredOpt(response.credentialOptions, createNew);
        const auth = createNew ? navigator.credentials.create(credentialOptions) : navigator.credentials.get(credentialOptions);
        auth.then(auth => {
            return authenticateKey(auth.id)})
        .then(authResponse => {
            if (authResponse.authSuccess) {
                showToast("Autenticacion exitosa, redireccionando a telegram. Si no funciona, haz click <a href='https://t.me/t_weather_wiz_bot'>aqui</a>", false, 60);
                setTimeout(() => {
                    window.location.href = 'tg://resolve?domain=https://t.me/t_weather_wiz_bot';
                }, 1500);
            } else {
                showToast("Autenticacion fallida, dispositivo no registrado.");
            }
        }).then(stopSpinner)
        .catch(error => {
            showToast("Error en la autenticacion, vuelve a intentar.");
            console.error(error)
            stopSpinner();
        });
    });
}

function formatCredOpt(credOpt, createNew) {
    const challenge = credOpt.publicKey.challenge;
    credOpt.publicKey.challenge = new Uint8Array(challenge).buffer;
    if (createNew) {
        const id = credOpt.publicKey.user.id;
        credOpt.publicKey.user.id = new Uint8Array(id).buffer;
    }
    return credOpt;
}

async function authenticateKey(key) {
    return await sendData("authenticateKey", { key, token, id });
}

function validateLink() {
    if (!token || !id) {
        showToast("Link invalido, abre el recibido por telegram.");
        return Promise.resolve(null);
    }
    return sendData("validateLink", { token, id });
}

async function sendData(action, data) {
    return fetch(apiUrl+action+"/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) return response.json();
        throw new Error("Network response was not ok.");
    })
    .catch(error => {
        showToast("Hubo un error en la conexion con el servidor, prueba de nuevo mas tarde.")
        console.error("There was a problem with the fetch operation:", error);
    });
}

function showToast(message, error = true, duration = 3) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    toastMessage.innerHTML = message;
    toast.classList.add(error ? "error" : "success");
    toast.classList.remove('hidden');
    setTimeout(hideToast, duration * 1000);
}

function hideToast() {
    const toast = document.getElementById('toast');
    toast.classList.add('hidden');
    toast.classList.remove("error", "success");
}

function startSpinner() {
    authenticateBtn.classList.add("spinner");
    authenticateBtn.blur();
    authenticateBtn.innerText = "";
}

function stopSpinner() {
    authenticateBtn.classList.remove("spinner");
    authenticateBtn.innerText = btnText;
}