document.addEventListener('DOMContentLoaded', async () => {
    const params = new URLSearchParams(window.location.search);
    const courseId = params.get("course_id");
    const topicId = params.get("topic_id");
    const question_id = params.get("question_id");

    // if (!courseId || !topicId || !difficulty) {
    //     alert("Missing query parameters.");
    //     return;
    // }

    const problemTitle = document.querySelector('.problem-title');
    const problemDescription = document.querySelector('.problem-description');
    const testCasesContainer = document.querySelector('.test-cases');
    const codeEditorTextarea = document.getElementById('code-editor');

    // Initialize CodeMirror
    const codeMirror = CodeMirror.fromTextArea(codeEditorTextarea, {
        mode: courseId.includes("python") ? "python" : "javascript",
        theme: "dracula",
        lineNumbers: true,
        indentUnit: 4,
        smartIndent: true,
        tabSize: 4,
        indentWithTabs: false,
        autoCloseBrackets: true,
        matchBrackets: true,
        styleActiveLine: true,
        lineWrapping: true,
        extraKeys: {
            "Tab": function(cm) {
                if (cm.somethingSelected()) {
                    cm.indentSelection("add");
                } else {
                    cm.replaceSelection("    ", "end", "+input");
                }
            },
            "Shift-Tab": function(cm) {
                cm.indentSelection("subtract");
            },
            "Ctrl-/": function(cm) {
                cm.toggleComment();
            },
            "Cmd-/": function(cm) {
                cm.toggleComment();
            }
        }
    });

    try {
        const res = await fetch(`http://localhost:8000/courses/${courseId}/topics/${topicId}/questions/${question_id}`);
        const problem = await res.json();
        console.log(problem)

        // Update UI with question details
        problemTitle.textContent = problem.title;
        problemDescription.textContent = problem.description;
        codeMirror.setValue(problem.starter_code.content);

        // Display visible test cases
        testCasesContainer.innerHTML = '<h3>Visible Test Cases</h3>';
        problem.test_cases.visible_cases.forEach((testCase, index) => {
            div = document.createElement('div');
            div.className = 'test-case';
            div.innerHTML = `
                <div><strong>Test Case ${index + 1}</strong></div>
                <div><strong>Input:</strong></div>
                <pre>${testCase.input}</pre>
                <div><strong>Expected Output:</strong></div>
                <pre>${testCase.expected_output}</pre>
            `;
            testCasesContainer.appendChild(div);
        });

    } catch (err) {
        console.error("Error loading problem:", err);
        problemTitle.textContent = "Error loading problem";
        problemDescription.textContent = "Unable to load the problem. Please try again later.";
    }
});
