function myFunction() {
/* Get the text field */
let copyText = document.getElementById("id_short_url");

/* Select the text field */
copyText.select();
copyText.setSelectionRange(0, 99999); /*For mobile devices*/

/* Copy the text inside the text field */
document.execCommand("copy");

/* Alert the copied text */
alert("URL copied to clipboard: " + copyText.value);
}
