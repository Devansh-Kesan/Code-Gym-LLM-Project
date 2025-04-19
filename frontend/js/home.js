document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("courses");
  
    try {
      const res = await fetch("http://localhost:8080/courses");
      const courses = await res.json();
  
      courses.forEach(course => {
        console.log(course); 
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `
          <h2>${course.title}</h2>
          <p>${course.description}</p>
          <p><strong>Difficulty:</strong> ${course.difficulty}</p>
          <p><strong>Language:</strong> ${course.language}</p>
          <p><strong>Time:</strong> ${course.estimated_hours} hrs</p>
        `;

        div.onclick = () => {
          window.location.href = `topics.html?course_id=${course.id}`;
        };
        container.appendChild(div);
      });
    } catch (err) {
      container.innerHTML = "<p>Failed to load courses. Please try again later.</p>";
      console.error("Error fetching courses:", err);
    }
  });
  