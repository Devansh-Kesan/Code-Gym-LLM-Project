document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const courseId = params.get("course_id");
    const topicId = params.get("topic_id");
  
    const container = document.getElementById("question-list");
    const titleEl = document.getElementById("topic-title");
    try {
      const res = await fetch(`http://localhost:8080/courses/${courseId}/topics/${topicId}`);
      const topic = await res.json();
      console.log(topic)
      titleEl.textContent = topic.topic_title;
  
      topic.questions.forEach((q, index) => {
        const div = document.createElement("div");
        div.className = "question-bar";
        div.innerHTML = `
          <div class="question-info">
            <span class="q-num">${index + 1}</span>
            <span class="q-title">${q.title}</span>
          </div>
          <div class="q-meta">
            <span class="q-difficulty">${q.complexity}</span>
            <button class="go-btn">Solve</button>
          </div>
        `;
  
        div.querySelector(".go-btn").onclick = () => {
          window.location.href = `editor.html?course_id=${courseId}&topic_id=${topic.topic_id}&question_id=${q.id}`;
        };
  
        container.appendChild(div);
      });
    } catch (err) {
      console.error("Failed to load questions:", err);
      container.innerHTML = "<p>Unable to load questions for this topic.</p>";
    }
  });
