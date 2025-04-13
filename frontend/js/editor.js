// Global DOM variables
const problemTitle = document.querySelector('.problem-title');
const problemCourse = document.querySelector('#course-name');
const problemTopic = document.querySelector('#topic-name');
const problemComplexity = document.querySelector('#complexity');
const problemDescription = document.querySelector('.problem-description');
const testCasesContainer = document.querySelector('.test-cases');
const codeEditorTextarea = document.getElementById('code-editor');
const hintBtn = document.getElementById("hint-btn");
const errorBtn = document.getElementById("error-btn");
const reviewBtn = document.getElementById("review-btn");
const testBtn = document.getElementById("test-btn");
const llmContent = document.getElementById("llm-content");
const llmResponse = document.getElementById("llm-response");
const params = new URLSearchParams(window.location.search);
const courseId = params.get("course_id");
const topicId = params.get("topic_id");
const question_id = params.get("question_id");

// console.log("A",courseId)
// console.log("B",topicId)
// console.log("C",question_id)


let codeMirror; // we'll initialize this later globally


async function initializeEditorPage() {
    // Init CodeMirror
    codeMirror = CodeMirror.fromTextArea(codeEditorTextarea, {
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
            "Tab": cm => cm.somethingSelected() ? cm.indentSelection("add") : cm.replaceSelection("    ", "end", "+input"),
            "Shift-Tab": cm => cm.indentSelection("subtract"),
            "Ctrl-/": cm => cm.toggleComment(),
            "Cmd-/": cm => cm.toggleComment()
        }
    });

    try {
        const [res, res1, res2] = await Promise.all([
            fetch(`http://localhost:8000/courses/${courseId}/topics/${topicId}/questions/${question_id}`),
            fetch(`http://localhost:8000/courses/${courseId}/topics/${topicId}`),
            fetch(`http://localhost:8000/courses/${courseId}/`)
        ]);

        const [problem, topic, course] = await Promise.all([res.json(), res1.json(), res2.json()]);

        // Populate UI
        problemTitle.textContent = problem.title;
        problemDescription.textContent = problem.description;
        problemCourse.textContent = course.title;
        problemTopic.textContent = topic.topic_title;
        problemComplexity.textContent = problem.complexity;
        codeMirror.setValue(problem.starter_code.content);

        // Test Cases
        testCasesContainer.innerHTML = '<h3>Visible Test Cases</h3>';
        problem.test_cases.visible_cases.forEach((testCase, index) => {
            const div = document.createElement('div');
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
}

function setupHintFeature() {
    if (!hintBtn) return;

    hintBtn.addEventListener("click", async () => {
        const code = codeMirror.getValue();
        // console.log(code)
        const title = problemTitle.textContent;
        const description = problemDescription.textContent;

        llmContent.textContent = "Generating hints...";
        llmResponse.style.display = "block";

        try {
            const response = await fetch("http://localhost:8000/llm/hint", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, description, code })
            });

            const data = await response.json();
            llmContent.textContent = data.hints;
        } catch (error) {
            llmContent.textContent = "Failed to get hints. Please try again.";
            console.error("Error fetching hint:", error);
        }
    });
}

function setupErrorExplanationFeature() {
    if (!errorBtn) return;

    errorBtn.addEventListener("click", async () => {
        const code = codeMirror.getValue();
        const title = problemTitle.textContent;
        const description = problemDescription.textContent;

        llmContent.textContent = "Analyzing error...";
        llmResponse.style.display = "block";

        try {
            const response = await fetch("http://localhost:8000/llm/explain-error", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, description, code })
            });

            const data = await response.json();
            llmContent.textContent = data.explanations;
        } catch (error) {
            llmContent.textContent = "Failed to analyze error. Please try again.";
            console.error("Error fetching error explanation:", error);
        }
    });
}

function setupTestCaseGenerationFeature() {
    if (!testBtn) return;

    testBtn.addEventListener("click", async () => {
        const code = codeMirror.getValue();
        const title = problemTitle.textContent;
        const description = problemDescription.textContent;

        llmContent.textContent = "Generating test cases...";
        llmResponse.style.display = "block";

        try {
            const response = await fetch("http://localhost:8000/llm/test-cases", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, description, code })
            });

            const data = await response.json();
            llmContent.textContent = data.test_cases;
        } catch (error) {
            llmContent.textContent = "Failed to generate test cases. Please try again.";
            console.error("Error generating test cases:", error);
        }
    });
}

function setupCodeReviewFeature() {
    if (!reviewBtn) return;

    reviewBtn.addEventListener("click", async () => {
        const code = codeMirror.getValue();
        const title = problemTitle.textContent;
        const description = problemDescription.textContent;

        llmContent.textContent = "Reviewing code...";
        llmResponse.style.display = "block";

        try {
            const response = await fetch("http://localhost:8000/llm/code-review", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, description, code })
            });

            const data = await response.json();
            llmContent.textContent = data.review;
        } catch (error) {
            llmContent.textContent = "Failed to review code. Please try again.";
            console.error("Error fetching review:", error);
        }
    });
}

const runBtn=document.getElementById("run-btn");
const SubBtn=document.getElementById("submit-btn");
const resultContainer=document.getElementById("results-container")
const resultContent=document.getElementById("results-content")

async function runCode(){
    if (!runBtn) return;
    runBtn.addEventListener("click",async ()=>{
        const code=codeMirror.getValue();
        // const questionId=params.get("question_id");
        // const courseId = params.get("course_id");
        // const topicId = params.get("topic_id");
        // const question_id = params.get("question_id");

        resultContent.textContent="Running Code...";
        resultContainer.style.display="block";

        try{
            const response=await fetch("http://localhost:8000/run-code",{
                method:"POST",
                headers:{ "Content-Type":"application/json" },
                body:JSON.stringify({code:code,question_id:question_id})
            });
            const data=await response.json();
            // console.log(data)
            //accordinglt update here what backend sends 

            let resultText="";
            if (data.test_results){
                data.test_results.forEach(test=>{
                    if (!test.passed){
                        resultText+=`Test case: ${test.test_name}\nError: ${test.error}\n\n`
                    }
                });
            }

            if (resultText==""){
                resultText="All visible test cases passed.";
            }

            resultContent.textContent=resultText;
            
        }
        catch(error){
            resultContent.textContent="Failed to run code. Please Try Again";
            console.error("Error running Code:", error);
        }

    })
}

async function Submit() {
    if (!SubBtn) return;
    SubBtn.addEventListener("click",async ()=>{
        const code=codeMirror.getValue();

        resultContainer.textContent="Running Code.."
        resultContent.style.display="block"

        try{
            const response=await fetch("http://localhost:8000/run-code-all",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({code:code,question_id:question_id})
            });

            const data=await response.json();

            let resultText="";
            if (data.total === data.passed){
                resultText="Accepted! All test cases passed";
            }else{
                data.test_results.forEach(test=>{
                    if (!test.passed){
                        resultText+=`Test case: ${test.test_name} \nError: ${test.error}`;
                    }
                    if (test.expected){
                        resultText+=`\nExpected: ${test.expected}`;
                    }
                    if (test.actual){
                        resultText+=`\nactual: ${test.actual}`;
                    }
                    resultText+=`\n\n`;
                });
            }
            resultContainer.textContent=resultText;
        }
        catch(error){
            resultContainer.textContent='Failed to run code. Please Try Again'
            console.error("Error runnning code ",error)
        }

    })
}


document.addEventListener('DOMContentLoaded', async () => {
    await initializeEditorPage();
    setupHintFeature();  // You can also call other feature functions here later
    setupErrorExplanationFeature();         // wire Error feature 
    setupTestCaseGenerationFeature();              // wire Test Case feature 
    setupCodeReviewFeature();               // wire Code Review feature 
    runCode();
    Submit();
    // console.log("mirrorval",codeMirror.getValue())
});
