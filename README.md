# PL Environment Diagram Element
This tool allows environment diagramming problems to be hosted and graded on [PrairieLearn](https://www.prairielearn.com/), an online assessment system. Environment diagrams are a kind of interactive program visualization exercise where students are asked to execute a program as a computer would and draw out a diagram representing the state of the computer. 

Our version of this tool is based on the diagramming and visual conventions of [PythonTutor](https://pythontutor.com/cp/composingprograms.html#mode=edit), a popular program visualization website. The styling of Python Tutor was originally released under an open-source license and is used with permission. 


<img src="[https://github.com/favicon.ico](https://github.com/user-attachments/assets/ff811f3e-8bed-479d-b099-71590abd2492)" width="400px" alt="An example problem of our tool on PrairieLearn">

## Demos
You can try out a [front-end-only version of our user interface](https://gabeclasson.github.io/pl-ucb-environmentdiagrams/frontend-demo.html),
which will allow you to create an environment diagram as a student would but will not allow you to save or grade it. 

We've also created demo videos for both the instructor and the student interfaces, which you can see below. 

## SIGCSE TS
We presented a poster about our tool at the SIGCSE Technical Symposium in February 2025. 
* Read our [submission at the ACM Digital Library](https://dl.acm.org/doi/10.1145/3641555.3705169)
* See our poster's [information page on the SIGCSE TS 2025 website](https://sigcse2025.sigcse.org/details/sigcse-ts-2025-posters/164/Dynamic-Randomizable-Autogradable-Visual-Programming-Simulations-for-Python-Using-P)

Noemi Chulo, Gabriel Classon, Ashley Chiu, Dan Garcia, Armando Fox, and Narges Norouzi. 2025. Dynamic, Randomizable, Autogradable Visual Programming Simulations for Python Using Prairielearn. In Proceedings of the 56th ACM Technical Symposium on Computer Science Education V. 2 (SIGCSETS 2025). Association for Computing Machinery, New York, NY, USA, 1419–1420. https://doi.org/10.1145/3641555.3705169

## Did you just have a course created for  you?

If so, this repo was used as a template, and your course repo's name should be `pl-SSS-CCC`, 
where `SSS` is your project
institution name (`ucb`, `csulb`, `ecc`) and `CCC` is the lowercase course
number at your institution (eg `pl-ucb-cs169a`, `pl-ecc-csci8`, etc).
    
We (UCB PL admins) should already have created a team
`pl-dev-SSS-CCC` that has write access to your repo; email us the
names of any course staff who should have access.  **WARNING:** your
repo will likely contain sensitive content such as exam questions.  Be
careful who has access.  **All access to PL repos is by teams**, not
by adding individuals, to keep access control manageable.

* Delete (meaning `git rm`) the `elements` subdirectory, unless you specifically want to use
the custom elements in here (see below for some documentation)
* Delete the contents of `serverFilesCourse` and `clientFilesCourse`
* Delete the contents of `courseInstances` (you'll add your own
later)
* Delete the contents of `questions/`, which will be replaced with
your course's questions
* Immediately update this `README.md` and `infoCourse.json` to
reflect the info for your course, including inserting a valid UUID for
the course.  You can run `uuidgen` at a shell prompt to make one.
**Important.** Just about every type of thing in PL -- course, question, element, etc. -- has a UUID (Universally Unique ID).  You can generate one by typing `uuidgen` at a terminal window or by using the [UUID generator](https://www.uuidgenerator.net). For safety, in the template repo all UUID values have been set to "9999...".  **In your new repo, immediately `git rm` any files you do not need, and in the files that remain, replace every UUID with a fresh one.**


**Note:** Although it has become customary to name the primary Git
branch `main` rather than `master`, **do not do so for PL repos** as
the server will not be able to sync them.  The server will only sync
to the `master` branch.

