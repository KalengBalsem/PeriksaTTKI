const user_input = document.querySelector('.input');
const response_block = document.querySelector('.response');
const input_form = document.querySelector('.input_form');
let responseInProgress = false;

// GLOBAL FUNCTIONS
function wrapMatchedWords(text, words) {
    for (let raw_word of words) {
        const word = raw_word.original;
        const regex = new RegExp(`\\b${word}\\b`, 'gi'); // Use word boundary and case-insensitive matching
        text = text.replace(regex, (match) => `<button class="wrong" popovertarget="${match}">${match}</button>`);
    }
    return text;
}

function setSuggestionPosition(event, suggestion) {
    const rect = event.target.getBoundingClientRect();
    const scrollTop = document.documentElement.scrollTop;
    const scrollLeft = document.documentElement.scrollLeft;
    const suggestionHeight = suggestion.offsetHeight;

    const top = rect.top + scrollTop + suggestionHeight + 10; // Positioning above the word with a small margin
    const left = rect.left + scrollLeft;

    suggestion.style.setProperty('top', `${top}px`);
    suggestion.style.setProperty('left', `${left}px`);
}

function getCorrections(originalWord, error_words) {
    for (let wordObj of error_words) {
        if (wordObj.original === originalWord) {
            return wordObj.correction;
        }
    }
    return null; // Return null if no matching original word is found
}

// SOME EPIC SHITs GOING ON HERE (send user_input and show response in the page)
input_form.addEventListener('submit', (event) => {
    event.preventDefault();
    send_user_input();
});

document.querySelector(".input").addEventListener("keypress", e => {
    if (e.key === "Enter" && !e.shiftKey) {
        if (responseInProgress) {
            e.preventDefault(); // Prevent Enter key action
        } else {
            e.preventDefault();
            send_user_input();
        }
    }
});

async function send_user_input() {
    const input = user_input.value.trim();
    if (input.length === 0) {
        return;
    }

    response_block.innerHTML = '';  // reset the response block
    
    // creating LOADING div (the algo can be optimized)
    const loader = document.createElement('p');
    loader.classList.add("loader");
    response_block.appendChild(loader);

    // disabling button temporarily
    const send_button = document.querySelector(".send_button");
    send_button.textContent = '--';
    send_button.disabled = true;

    // disabling press enter key
    responseInProgress = true;

    // RECEIVING DYNAMIC DATA FROM DJANGO
    fetch('', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          'data_type': 'user_input',
          'user_input': input
        })
      })
      .then(response => response.json())
      .then(data => {
        // accepting and assigning responses
        const typo_words = data.typo_words;
        const error_words = data.error_words;
        const paraphrase = data.paraphrase;
        const typoParagraph = document.createElement('p');
        typoParagraph.classList.add('wrong_text');
        const paraphraseParagraph = document.createElement('p');
        typoParagraph.innerHTML = typo_words;
        paraphraseParagraph.innerHTML = paraphrase;

        // create response subheadings 
        const typoSubheading = document.createElement('p');
        const paraphraseSubheading = document.createElement('p');
        typoSubheading.classList.add('sub_heading')
        paraphraseSubheading.classList.add('sub_heading')
        typoSubheading.textContent = `Typo`;
        paraphraseSubheading.textContent = `Parafrase`;

        // labelling error_words
        typoParagraph.innerHTML = wrapMatchedWords(typoParagraph.textContent, error_words);

        // remove LOADING
        loader.classList.remove("loader");
        // append subheadings and responses
        response_block.appendChild(typoSubheading);
        response_block.appendChild(typoParagraph);
        response_block.appendChild(paraphraseSubheading);
        response_block.appendChild(paraphraseParagraph);

        // showing correction word suggestions
        const suggestion = document.querySelector('.suggestion');
        const suggestion_list = document.querySelector('.suggestion_list');

        function showSuggestions(element, suggestions) {
            suggestion_list.innerHTML = '';
            suggestions.forEach(suggestion => {
                const button = document.createElement('button');
                button.textContent = suggestion;
                suggestion_list.appendChild(button);
            });
        }

        typoParagraph.addEventListener('click', event => {
            suggestion_list.innerHTML = '';
        
            const popover_target = event.target.getAttribute('popovertarget');
            suggestion.setAttribute('id', popover_target)
        
            if (event.target.classList.contains('wrong')) {
                const word = popover_target;
                showSuggestions(event.target, getCorrections(word, error_words));
                setSuggestionPosition(event, suggestion);
            }
        });

        // re-enable button
        send_button.textContent = '>';
        send_button.disabled = false;

        // re-enable press enter key
        responseInProgress = false;
      });
}

async function sendData() {
    const button = document.querySelector('.submit_correction');
    button.disabled = true;

    // assigning data to variable
    const original_word = document.querySelector('.suggestion').getAttribute('id');
    const user_correction = document.querySelector('.user_correction').value;
    const data = {original_word, user_correction};

    try {
        const response = await fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'data_type': 'user_correction',
                'user_correction': JSON.stringify(data)
              })
        });
        // Check if the request was successful
        if (response.ok) {
            const result = await response.json();
            console.log(result);
        } else {
            console.log(response.statusText);
        }
    } catch (error) {
        console.log(error.message);
    } finally {
        // Re-enable the button
        button.disabled = false;
        document.querySelector('.user_correction').value = '';

         // Show the thank you message
        const thankyou_alert = document.querySelector('.thankyou_alert');
        thankyou_alert.textContent = 'Terima kasih atas masukannya!';

         // Hide the thank you message after 3 seconds
         setTimeout(() => {
            thankyou_alert.textContent = '';
         }, 5000);
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && event.target.classList.value == 'user_correction') {
        sendData();
    }
}