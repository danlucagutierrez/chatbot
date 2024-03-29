const authenticateBtn = document.getElementById('authenticateBtn');
const statusMessage = document.getElementById('statusMessage');
const originalID = document.getElementById('originalID');
const newID = document.getElementById('newID');

const randomUserId = new Uint8Array(16);
// crypto.getRandomValues(randomUserId); // Generate a random user ID, disabled to avoid creating multiple during testing
let storedCredential = null; // Variable to store the credential
const originalContent = authenticateBtn.textContent
authenticateBtn.addEventListener('click', async () => {
    if (!window.PublicKeyCredential) {
        console.log("Error: Cliente no compatible, por favor prueba con otro browser o dispositivo")
    }
    authenticateBtn.textContent = "Loading..."
    const challenge = crypto.getRandomValues(new Uint8Array(32));
    console.log("starting biometrics")
    try {
        if (!storedCredential) {
            // If no stored credential, create a new one
            storedCredential = await navigator.credentials.create({
                publicKey: {
                    challenge: challenge, // Generate a random challenge
                    rp: { name: 'WeatherWiz' },
                    user: { id: randomUserId, name: 'user@example.com', displayName: 'User' },
                    pubKeyCredParams: [
                        { type: 'public-key', alg: -7 },  // ES256
                        { type: 'public-key', alg: -257 }  // RS256
                    ],
                    authenticatorSelection: { authenticatorAttachment: 'platform' },
                    timeout: 60000, // Timeout in milliseconds
                    attestation: 'direct'
                }
            });
            originalID.textContent = storedCredential.id;
        } else {
            // If there's a stored credential, use it for authentication
            storedCredential = await navigator.credentials.get({
                publicKey: {
                    challenge: challenge, // Generate a new challenge
                    timeout: 60000, // Timeout in milliseconds
                }
            });
            newID.textContent = storedCredential.id;
        }

        // Authentication successful
        /**
         * Aca se tendria que enviarse la public key
         * para que el back secargue de devolver un
         * true o false segun corresponda
         */

        // Validation successful
        console.log("Auth successful")
        statusMessage.textContent = 'Authentication successful!';
        console.log(storedCredential.id);
        authenticateBtn.textContent = "Autenticacion Exitosa"
        authenticateBtn.classList.remove("error")
        authenticateBtn.classList.add("success")
        setTimeout( () => {
            console.log("Valid successful")
            authenticateBtn.textContent = originalContent
            authenticateBtn.classList.remove("success")
            window.location.href = "https://t.me/t_weather_wiz_bot"
        }, 1500)
    } catch (error) {
        // Handle authentication errors
        console.log("Auth failed")
        authenticateBtn.textContent = "Error en la autenticacion"
        authenticateBtn.classList.add("error")
        statusMessage.textContent = 'Authentication failed: ' + error.message;
        console.error(error);
        setTimeout( () => {
            authenticateBtn.textContent = originalContent
            authenticateBtn.classList.remove("error")
        }, 2500)
    }
});