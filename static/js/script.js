// Hide flash messages after 2secs
setTimeout(() => {
    flash_message = document.getElementsByClassName("flash");
    for (let i = 0; i < flash_message.length; i++) {
        flash_message[i].style.display = "none";
    }
}, 2000);