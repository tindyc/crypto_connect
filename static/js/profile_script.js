// Tabs code from W3S
function openTab(evt, tabName) {
    let i,
        tabcontent, 
        tablinks;
  
    // Change to display first tab on page load
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
  
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }
  
  openProfileTabOnload();
  // Open first tab on page load
  function openProfileTabOnload()  {
      document.getElementById("profile").style.display = "block";
      document.getElementsByClassName("tablinks")[0].classList.add("active");
  }