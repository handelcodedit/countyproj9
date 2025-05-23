function getCookie(name) {
    let cookieArr = document.cookie.split(";");
    for (let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if (name === cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}

function setSessionId() {
    const sessionId = getCookie("session_id");
    if (sessionId) {
        const sessionInput = document.getElementById("session_id");
        if (sessionInput) {
            sessionInput.value = sessionId;
        }
    }
}

window.onload = setSessionId;
