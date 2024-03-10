function getLastIndex(slug) {
  let index;
  let prevFrames = executionVisualizer.querySelectorAll('[id^="'+slug+'"]')
  let lastFrame = prevFrames[prevFrames.length - 1]
  if (!lastFrame) {
    index = 0 // This should never happen.
  } else {
    let str = lastFrame.id.substring(slug.length)
    let indexOfDash = str.indexOf("-");
    if (indexOfDash >= 0) {
      str = str.substring(0, indexOfDash)
    }
    index = parseInt(str) + 1
  }
  return index
}

function add_variable_listener(e) {
  console.log(e)
  button = e.target
  frame = button.closest(".stackFrame")
  variables = frame.querySelector(".stackFrameVarTable")
  let index = getLastIndex(frame.id + "-var-")
	//var newvar = document.createElement("div");
  if (frame.id == "frame-0") {
    variables.appendChild(make_variable(frame.id + "-var-" + index))
  } else {
    returnVal = frame.querySelector(".returnValueTr");
    variables.insertBefore(make_variable(frame.id + "-var-" + index), returnVal)
    updatePointerFrom(frame.id + "-return-val", false)
  }
}

function make_variable(plKey, returnValue=false) {
  const tr = document.createElement("tr");
  tr.classList.add("variableTr", "removable")
  tr.id = plKey
  var varname; 
  if (returnValue) {
    tr.classList.add("returnValueTr")
    varname = document.createElement("span")
    varname.innerText = "Return Value"
  } else {
    varname = make_variable_length_input("stackFrameVarInput", plKey + "-name")
  }
  var stackframeval = make_value_box("stackFrameValueInput", plKey + "-val")

  var td = tr.insertCell();
  td.classList.add()
  if (!returnValue) {
    td.appendChild(make_remove_button(tr));
  }
  var td = tr.insertCell();
  td.classList.add("stackFrameVar")
  td.appendChild(varname);
  var td = tr.insertCell();
  td.classList.add("stackFrameValue")
	td.appendChild(stackframeval);
  return tr;
}

function make_remove_button(target) {
  var removeframe = document.createElement("button");
  removeframe.classList.add("btn", "removeButton")
  removeframe.type = "button";
  removeframe.addEventListener("click", removeListener)
  return removeframe
}

function removeListener(e) {
  let button = e.target
  let target = button.closest(".removable")

  // if (target.classList.contains("topLevelHeapObject")) {
  //   updatePointersTo(target.id, true)
  // } else if (target.classList.contains("stackFrame")) {
  //   for (let input of Array.from(document.getElementsByClassName("stackFrameValueInput"))) {
  //     updatePointerFrom(input.id, true)
  //   } 
  // } else if (target.classList.contains("variableTr")) {
  //   updatePointerFrom(target.getElementsByClassName("stackFrameValueInput")[0].id, true)
  // }

  target.parentElement.removeChild(target);
  updateAllPointers()
}

function updateAllPointers() {
  for (let pointer of Array.from(document.getElementsByClassName("pointerArrow"))) {
    updatePointer(pointer)
  }
}

function updatePointersTo(destinationId, remove) {
  for (let pointer of Array.from(document.getElementsByClassName("pointer-to-" + destinationId))) {
    console.log(pointer)
    if (remove) {
      removePointer(pointer)
    } else {
      updatePointer(pointer)
    }
  }
}

function updatePointerFrom(originId, remove) {
  let pointer = document.getElementById("pointer-from-" + originId);
  if (pointer == null) {
    return
  }
  if (remove) {
    removePointer(pointer)
  } else {
    updatePointer(pointer)
  }
}

function make_parent_marker(elemType, plKey) {
  var frame_parent_input = make_variable_length_input("frameParentHeader", plKey + "-parent")
  marker = document.createElement(elemType)
  marker.innerHTML = " [Parent = ";
  marker.type = "text";
  marker.appendChild(frame_parent_input);
  marker.innerHTML += "]";
  return marker
}

function make_value_box(className, plKey) {
  let container = document.createElement("div")
  container.className = "valueContainer"
  container.appendChild(make_variable_length_input(className, plKey))
  let pointerButton = document.createElement("button");
  pointerButton.className = "btn pointerButton pointerValueButton"
  pointerButton.type = "button"
  pointerButton.addEventListener("click", pointerValueToggleListener)
  container.appendChild(pointerButton)
  return container
}

function make_variable_length_input(className, plKey) {
  let input = document.createElement("input")
  input.classList.add(className, "pl-html-input")
  input.id = plKey
  input.name = plKey
  input.value = ""
  input.setAttribute("data-instavalue", "submittedValues." + plKey)
  input.addEventListener("keyup", function () {
    updateInputLengthToContent(input)
  });
  input.addEventListener("keydown", function () {
    updateInputLengthToContent(input)
  });
  return input
}

function updateInputLengthToContent(input) {
  let oldWidth = window.getComputedStyle(input).width
  input.style.minWidth = (input.value.length + 1) + "ch"
  if (window.getComputedStyle(input).width != oldWidth) {
    updateAllPointers()
  } 
}

function add_frame() {
  let index = getLastIndex("frame-")
	var frame = document.createElement("div");
  var frame_name_label = document.createElement("label");
  var frame_name = make_variable_length_input("frameHeader", "frame-" + index + "-name")
  var variables = document.createElement("table");
  var variable_button = document.createElement("button");
  var test = document.createElement("div");
  
  frame.classList.add("stackFrame", "removable");
  frame_name_label.className = "frameHeader";
  
  test.className = "stackFrameValue";
  
  variables.className = "stackFrameVarTable";

  let removeframe = make_remove_button(frame);
  
  variable_button.className = "btn"
  variable_button.type = "button"
  variable_button.innerHTML = "add variable";
  variable_button.onclick = add_variable_listener


  frame_name_label.innerHTML = "f" + index + ": ";
  frame_name_label.inner
  variables.appendChild(make_variable("frame-" + index + "-return", true))

  frame.id = "frame-" + index
  
  //frame.appendChild(test);
  frame.appendChild(removeframe);
  frame.appendChild(frame_name_label);
  frame.appendChild(frame_name);
  frame.appendChild(make_parent_marker("label", "frame-" + index));
  frame.appendChild(variables);
  frame.appendChild(variable_button);

  executionVisualizer.querySelector("#globals_area").appendChild(frame);
  return frame
  //document.body.appendChild(frame);
}

function add_heap_object(id, content, typeName) {
  let topLevelHeapObject = document.createElement("div")
  topLevelHeapObject.classList.add("topLevelHeapObject", "removable")
  topLevelHeapObject.id = id;
  let heapObject = document.createElement("div")
  heapObject.className = "heapObject";
  topLevelHeapObject.appendChild(heapObject)
  topLevelHeapObject.appendChild(make_remove_button(topLevelHeapObject))
  if (typeName) {
    let typeMarker = document.createElement("div")
    typeMarker.className = "typeLabel"
    typeMarker.innerText = typeName
    heapObject.append(typeMarker)
  }
  heapObject.appendChild(content)
  executionVisualizer.querySelector("#heap").appendChild(topLevelHeapObject);
}

function add_function_object() {
  let index = getLastIndex("heap-func-")
  let funcObj = document.createElement("div")
  funcObj.classList.add("funcObj")
  funcObj.innerText = "func "
  let funcNameInput = make_variable_length_input("funcNameInput", "heap-func-" + index + "-name")
  funcObj.appendChild(funcNameInput)
  funcObj.appendChild(make_parent_marker("span"), "heap-func-" + index)

  add_heap_object("heap-func-" + index, funcObj, "function")
}

let vizLayoutTd;

function pointerValueToggleListener(e) {
  let button = e.target
  if (button.classList.contains("pointerButton")) {
    handlePointerClick(button);
  } else {
    handleValueClick(button);
  }
}

function handlePointerClick(button) {
  let valueContainer = button.closest(".valueContainer")
  let valueInput = valueContainer.children[0]
  let svg_objs = make_arrow_svg("pointer-from-" + valueInput.id)
  let svg = svg_objs[0]

  function mouseListener(mouseEvent) {
    let coords = relative_coordinates_obj_to_pointer(valueContainer, mouseEvent)
    update_arrow_svg(coords, svg_objs)
  }
  document.addEventListener("mousemove", mouseListener)
  vizLayoutTd.appendChild(svg)

  function clickListener(clickEvent) {
    clickEvent.stopPropagation()
    document.removeEventListener("mousemove", mouseListener)
    let targetObj = clickEvent.target.closest(".topLevelHeapObject")
    if (targetObj == null) {
      vizLayoutTd.removeChild(svg)
      return 
    } 
    svg.classList.add( "pointer-to-" + targetObj.id)
    valueInput.disabled = true
    valueInput.style.visibility = "hidden"
    valueInput.value = "#" + targetObj.id
    valueInput.style.width = ""
    button.classList.add("valueButton")
    button.classList.remove("pointerButton")
    update_arrow_svg(relative_coordinates_obj_to_obj(valueContainer, targetObj), svg_objs)
  }
  document.addEventListener("click", clickListener, {
    capture: true,
    once: true
  })
}

function handleValueClick(button) {
  let valueContainer = button.closest(".valueContainer")
  let valueInput = valueContainer.children[0]
  let pointerObj = document.getElementById("pointer-from-" + valueInput.id)
  removePointer(pointerObj)
}

function relative_coordinates_obj_to_pointer(obj1, mouseEvent) {
  let origin = vizLayoutTd.getBoundingClientRect()
  let pos1 = obj1.getBoundingClientRect()
  let x1 = pos1.x - origin.x + pos1.width/2
  let y1 = pos1.y - origin.y + pos1.height/2
  let x2 = mouseEvent.clientX - origin.x
  let y2 = mouseEvent.clientY - origin.y
  return [x1, y1, x2, y2]
}

function relative_coordinates_obj_to_obj(obj1, obj2) {
  let origin = vizLayoutTd.getBoundingClientRect()
  let pos1 = obj1.getBoundingClientRect()
  let pos2 = obj2.getBoundingClientRect()
  let x1 = pos1.x - origin.x + pos1.width/2
  let y1 = pos1.y - origin.y + pos1.height/2
  let x2 = pos2.x - origin.x
  let y2 = pos2.y - origin.y + pos2.height/2
  return [x1, y1, x2, y2]
}

function update_arrow_svg(coords, svg_objs) {
  let x1 = coords[0]
  let y1 = coords[1]
  let x2 = coords[2]
  let y2 = coords[3]
  let svg = svg_objs[0]
  let path = svg_objs[1]
  width = Math.abs(x2 - x1)
  height = Math.abs(y2 - y1)
  let originX = Math.min(x1, x2)
  let originY = Math.min(y1, y2)
  svg.style.height = height + "px"
  svg.style.width = width + 'px'
  svg.style.top = originY
  svg.style.left = originX
  svg.setAttribute("width", width)
  svg.setAttribute("height", height)
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`)
  path.setAttribute("d", `M ${x1 - originX}, ${y1 - originY} L ${x2 - originX} ${y2 - originY}`)
}

function updatePointer(svg) {
  if (svg == null) {
    return
  }
  let path = svg.children[0]
  let originId = svg.id.substring("pointer-from-".length)
  let originElement = document.getElementById(originId)
  let destinationId;
  for (let className of svg.classList) {
    if (className.indexOf("pointer-to-") >= 0) {
      destinationId = className.substring("pointer-to-".length)
    }
  }
  let destinationElement = document.getElementById(destinationId)
  if (originElement == null || destinationElement == null) {
    removePointer(svg)
    return;
  }
  update_arrow_svg(relative_coordinates_obj_to_obj(originElement, destinationElement), [svg, path])
}

function removePointer(svg) {
  svg.parentElement.removeChild(svg)
  let originId = svg.id.substring("pointer-from-".length)
  let valueInput = document.getElementById(originId)
  if (valueInput != null) {
    valueInput.disabled = false
    valueInput.style.visibility = "visible"
    valueInput.value = ""
    valueInput.sib
    let button = valueInput.nextElementSibling
    button.classList.add("pointerButton")
    button.classList.remove("valueButton")
  }
}

function make_arrow_svg(id) {
  let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
  svg.setAttribute('class', "pointerArrow")
  svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
  svg.setAttribute('id', id)
  let newPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svg.appendChild(newPath)
  return [svg, newPath]
}

function add_list_object() {
  let index = getLastIndex("heap-list-")
  let listObj = document.createElement("table")
  listObj.className = "listTbl"
  let listHeaderRow = document.createElement("tr")
  let listContentsRow = document.createElement("tr")
  listObj.appendChild(listHeaderRow)
  listObj.appendChild(listContentsRow)
  let appendButton = make_add_button(function () {
    
  })
  listObj.id = "heap-list-" + index
  add_heap_object(listObj, "list")
}

function decrement_list_header(listHeaderObj) {
  if (!listHeaderObj.lastChild) {
    return;
  }
  listHeaderObj.removeChild(listHeaderObj.lastChild)
}

function increment_list_header(listHeaderObj) {
  let lastHeader = listHeaderObj.lastChild
  if (!lastHeader) {
    listHeaderObj.appendChild(make_list_header_object(0))
  }
  let lastNum = parseInt(lastHeader.innerText)
  listHeaderObj.appendChild(make_list_header_object(lastNum + 1))
}

function make_list_header_object(number) {
  let obj = document.createElement("td")
  obj.className = "listHeader"
  obj.innerText = "" + number
  return obj
}

function make_add_button(onclick) {
  var addButton = document.createElement("button");
  addButton.classList.add("btn", "addButton")
  addButton.type = "button";
  addButton.onclick = onclick
  return removeframe
}

let executionVisualizer;

window.addEventListener('load', function() {
  vizLayoutTd = document.getElementById("vizLayoutTdSecond")
  executionVisualizer = document.querySelector('.ExecutionVisualizerActive')
  if (executionVisualizer) {
    executionVisualizer.querySelectorAll('.addVarButton').forEach(x => x.addEventListener("click", add_variable_listener))
    executionVisualizer.querySelectorAll('.removeButton').forEach(x => x.addEventListener("click", removeListener))
    executionVisualizer.querySelector("#addFrameButton").addEventListener("click", add_frame)
    executionVisualizer.querySelector("#addFuncButton").addEventListener("click", add_function_object)
    executionVisualizer.querySelector("#addListButton").addEventListener("click", add_list_object)
  }
});