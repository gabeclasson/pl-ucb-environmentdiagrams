function add_variable(e) {
  console.log(e)
  button = e.target
  frame = button.closest(".stackFrame")
  variables = frame.querySelector(".stackFrameVarTable")
	//var newvar = document.createElement("div");
  const tr = variables.insertRow();
  tr.classList.add("variableTr")
  var removevar = document.createElement("button");
  var varname = document.createElement("input");
  var stackframeval = document.createElement("input");
  
  removevar.innerHTML = "x";
  removevar.onclick = function(){variables.deleteRow(tr)};

  
  /*newvar.appendChild(removevar);
  newvar.appendChild(varname);
  newvar.appendChild(stackframeval);*/
  var td = tr.insertCell();
  td.classList.add()
  td.appendChild(removevar);
  var td = tr.insertCell();
  td.classList.add("stackFrameVar")
  td.appendChild(varname);
  var td = tr.insertCell();
  td.classList.add("stackFrameValue")
	td.appendChild(stackframeval);
	//variables.appendChild();
}

function add_frame() {
	var frame = document.createElement("div");
  var removeframe = document.createElement("button");
  var frame_name_label = document.createElement("label");
  var frame_name = document.createElement("input");
  var variables = document.createElement("table");
  var variable_button = document.createElement("button");
  var variable_count = 0;
  var test = document.createElement("div");
  
  frame.className = "stackFrame";
  frame_name_label.innerHTML = "frame name: ";
  frame_name_label.className = "frameHeader";
  //frame_name.innerHTML = name;
  frame_name.className = "frameHeader";
  
  test.className = "stackFrameValue";
  
  variables.className = "frameTable";
  removeframe.innerHTML = "x";
  removeframe.onclick = function() {
    // Remove the frame when the button is clicked
    frame.removeChild(frame);
};  
  variable_button.innerHTML = "add variable";
  variable_button.onclick = function(){
    add_variable(variables); 
    variable_count = variable_count + 1;
    };
  
  //frame.appendChild(test);
  frame.appendChild(removeframe);
  frame.appendChild(frame_name_label);
  frame.appendChild(frame_name);
  frame.appendChild(variables);
  frame.appendChild(variable_button);
  document.getElementById("globals_area").appendChild(frame);
  //document.body.appendChild(frame);
}

let globalFrame = document.getElementById("globalFrame")
globalFrame.querySelector(".addVarButton").addEventListener("click", add_variable)
document.querySelector("#addFrameButton").addEventListener("click", add_frame)