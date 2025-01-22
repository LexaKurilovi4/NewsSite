const search_element = document.querySelector("header .search input")

tags = null

const add_mouse_listener = () => {
	images = document.querySelectorAll(".news-list li img")
	titles = document.querySelectorAll(".news-list li a")	
	const map_title_image = new Map()
	for (image of images) {
    	id = image.dataset.id
    	for (title of titles) {
    		if (title.dataset.id == id) {
    			map_title_image.set(id, [image, title])
    			break;
    		}
    	}
	}
	map_title_image.forEach((value) => {
		value[1].addEventListener("mouseover", () => value[0].classList.add("hover"))
		value[1].addEventListener("mouseout", () => value[0].classList.remove("hover"))
	})
}

const send_search_request = async (url, data) => {
	const resp = await fetch(url, {
		method: "GET", 
		headers: {
			"Content-Type":"application/json"
		},
		body: data
	})
	return resp
}

const on_search_click = async (event) => {
	if (!!tags) {
		return
	}
	url = window.location.href
	host = url.slice(0, url.indexOf("/", 7)) + "/tags/"
	data = null
	tags_data = await send_search_request("/tags/", data)
	tags = await tags_data.json()
	tags.categories = tags.categories.split(';')
	tags.tags = tags.tags.split(';')
}

const add_prompt = (data) => {
	const search_container = document.querySelector("header .search")
	search_url = search_element.dataset.url.slice(0, -3)
	if (search_container.lastElementChild.tagName == "UL") {
		search_container.lastElementChild.remove()
	}
	const list = document.createElement("ul")
	let text_html = ""
	for (item of data.categories) {
		text_html = text_html + `<li>
									<a href="${search_url+item}">
										<div class="prompt">${item}</div>
									</a>
								</li>\n`
	}
	list.innerHTML = text_html
	search_container.appendChild(list)
}

const on_search_change = (event) => {
	const search_container = document.querySelector("header .search")
	text = event.target.value
	if (text.length < 3) {
		if (search_container.lastElementChild.tagName == "UL") {
			search_container.lastElementChild.remove()
		}
		return
	}
	const pattern = new RegExp("[a-zA-Z]*"+text+"[a-zA-Z]*")
	search_objects = {"categories": [], "tags": []} 

	for (item of tags.categories) {
		if (pattern.exec(item)) {
			search_objects.categories = [...search_objects.categories, pattern.exec(item).input]
		}
	}

	for (item of tags.tags) {
		if (pattern.exec(item)) {
			search_objects.tags = [...search_objects.tags, pattern.exec(item).input]
		}
	}

	add_prompt(search_objects)
}

const search = (event) => {

}

document.addEventListener("DOMContentLoaded", () => add_mouse_listener())

search_element.addEventListener("click", () => on_search_click())
search_element.addEventListener("input", (e) => on_search_change(e))
