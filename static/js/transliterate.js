google.load("elements", "1", {
    packages: "transliteration"
});


var transliterationControl;
function onLoad() {
  var options = {
      sourceLanguage: 'en',
      destinationLanguage: ['hi','bn','sa','te'],
      transliterationEnabled: true,
      shortcutKey: 'ctrl+g'
  };
  // Create an instance on TransliterationControl with the required
  // options.
  transliterationControl =
    new google.elements.transliteration.TransliterationControl(options);

  // Enable transliteration in the textfields with the given ids.
  transliterationControl.makeTransliteratable(['id_title']);

}


// Handler for dropdown option change event.  Calls setLanguagePair to
// set the new language.
function languageChangeHandler() {
  var dropdown = document.getElementById('language');
  if (dropdown.options[dropdown.selectedIndex].value == 'en') {
    if (transliterationControl.isTransliterationEnabled() == true) {
      transliterationControl.toggleTransliteration();
    }
  }
  else {
    if (transliterationControl.isTransliterationEnabled() == false){
      transliterationControl.toggleTransliteration();
    }
    transliterationControl.setLanguagePair(
        google.elements.transliteration.LanguageCode.ENGLISH,
        dropdown.options[dropdown.selectedIndex].value);
  }
}

google.setOnLoadCallback(onLoad);


// $(document).ready(function() {
//     $('.dropdown-menu .dropdown-item').click(function() {
//       var x = $(this).text();
//       var y = $(this).attr('id');
//       console.log(y);
//       $(this).parent().parent().children().filter('button').text(x)
//       $(this).parent().parent().children().filter('input').val(y);
//     });
//   });
