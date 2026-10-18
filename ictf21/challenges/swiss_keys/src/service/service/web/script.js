function display(json, form) {
  for(const [key, val] of Object.entries(json)) {
    let input = form.querySelector('[name=' + key + ']')
    if(input) input.value = val
  }

  let msg = form.querySelector('.message')
  msg.textContent = json['message']

  document.getElementById('dst').style.display = 'block'
  document.getElementById('src').style.display = 'none'
}

function collect(form) {
  let json = {}
  for(const input of form.getElementsByTagName('input')) {
    const key = input.name
    if(!key) continue

    let val = input.value
    if(val === '') continue

    if(input.type == 'number') {
      val = parseInt(val, 10)
    }

    json[key] = val
  }

  return json
}

// Bind to the source form...
let form = document.getElementById('src')
form.addEventListener('submit', function(event) {
  event.preventDefault()

  let json = collect(event.target)

  let xhr = new XMLHttpRequest()
  xhr.onreadystatechange = function() {
    if(xhr.readyState !== 4) return

    if(xhr.status === 200) {
      let form = document.getElementById('dst')
      let json = JSON.parse(xhr.responseText)
      display(json, form)
    }
    else {
      let msg = form.querySelector('.message')
      msg.textContent = xhr.responseText
    }
  }

  console.log(json)
  xhr.open('POST', event.target.action)
  xhr.setRequestHeader('Content-Type', 'application/json')
  xhr.send(JSON.stringify(json))

  return false
})
