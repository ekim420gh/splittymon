function loading(){
  var element = document.getElementById('file-name');
  filename = element.innerText || element.textContent;
  if (String(filename) == "No file uploaded"){
    alert("Upload a file first")
  } else {

    // parent
    var parent = document.getElementById('upload-and-load');

    // new child
    var load_button = document.createElement("button");
    load_button.classList.add('button', 'is-primary', 'is-outlined', 'is-loading');

    // appent new child to parent
    parent.appendChild(load_button)
  }
}
