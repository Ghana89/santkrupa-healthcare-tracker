// ============================================================================
// PRESCRIPTION TEMPLATE FUNCTIONALITY
// ============================================================================

console.log("✨ Prescription Templates Script Loaded (executing immediately)");

// Execute immediately since this is loaded at end of page (after DOM is ready)
(function() {
    console.log("🚀 Prescription Templates Init - DOM Ready");

    // ---------- SAVE PRESCRIPTION AS TEMPLATE ----------
    const saveTemplateBtn = document.getElementById("save-template-btn");
    const saveTemplateModal = document.getElementById("save-template-modal");
    const saveTemplateForm = document.getElementById("save-template-form");
    const templateSearch = document.getElementById("template_search");
    const clinicSlug = templateSearch ? templateSearch.dataset.clinicSlug : null;
    
    console.log("🔧 Setup - Clinic Slug:", clinicSlug);
    console.log("✓ Save template button found:", !!saveTemplateBtn);
    console.log("✓ Template search element found:", !!templateSearch);
    
    // DEBUG: Log the templateSearch element details
    if (templateSearch) {
        console.log("📋 Template Search Element Details:");
        console.log("   - ID:", templateSearch.id);
        console.log("   - Value:", templateSearch.value);
        console.log("   - Data-clinic-slug:", templateSearch.dataset.clinicSlug);
        console.log("   - Placeholder:", templateSearch.placeholder);
    } else {
        console.error("❌ CRITICAL: Template search element NOT found!");
    }

    if (saveTemplateBtn) {
        console.log("✓ Save template button found");
        saveTemplateBtn.addEventListener("click", function() {
            console.log("💾 Opening save template modal");
            saveTemplateModal.style.display = "flex";
        });
    }

    if (saveTemplateForm && clinicSlug) {
        console.log("✓ Save template form found");
        saveTemplateForm.addEventListener("submit", function(e) {
            console.log("📤 Submitting save template form");
            e.preventDefault();

            const formData = new FormData(this);
            const prescriptionId = document.querySelector('[name="action"][value="add_medicine"]')?.parentElement?.closest('[data-prescription-id]')?.dataset.prescriptionId 
                                   || window.location.pathname.split('/').reverse()[2];

            const saveUrl = `/clinic/${clinicSlug}/doctor/prescription/${prescriptionId}/save-as-template/`;
            console.log("🔗 Saving to URL:", saveUrl);

            fetch(saveUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                console.log("📥 Save Template Response:", data);
                if (data.success) {
                    console.log("✅ Template saved successfully");
                    alert(data.message);
                    saveTemplateModal.style.display = "none";
                    saveTemplateForm.reset();
                } else {
                    console.error("❌ Save template failed:", data);
                    alert("Error: " + data.error);
                }
            })
            .catch(err => {
                console.error("❌ Save template fetch error:", err);
                alert("Server error while saving template");
            });
        });
    }

    // ---------- TEMPLATE SEARCH & LOAD ----------
    // NOTE: Using the same templateSearch already defined above
    const templateSuggestions = document.getElementById("template_suggestions");
    let templateLoadTimeout;

    console.log("🔄 Setting up template search listener...");
    
    if (templateSearch) {
        console.log("✓ Template search input found for event listener");
        console.log("  Clinic Slug:", clinicSlug);
        console.log("  Suggestions container:", !!templateSuggestions);
        
        templateSearch.addEventListener("input", function() {
            console.log("🔍 Template search input event fired:", this.value);
            clearTimeout(templateLoadTimeout);
            const query = this.value.trim();

            console.log("📝 Query after trim:", query);

            if (!query) {
                console.log("⚠️ Query is empty, hiding suggestions");
                templateSuggestions.style.display = "none";
                return;
            }

            templateLoadTimeout = setTimeout(() => {
                const searchUrl = `/clinic/${clinicSlug}/doctor/templates/search/?q=${encodeURIComponent(query)}`;
                console.log("🔗 Searching templates at:", searchUrl);
                
                fetch(searchUrl, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                })
                .then(res => res.json())
                .then(data => {
                    console.log("📥 Template Search Response:", data);
                    if (data.templates && data.templates.length > 0) {
                        console.log(`✅ Found ${data.templates.length} templates`);
                        let html = '<div style="background:white; border:1px solid #ccc; border-radius:6px; overflow:hidden;">';
                        data.templates.forEach(template => {
                            html += `
                            <div style="padding:10px; border-bottom:1px solid #eee; cursor:pointer; background-color:#fff; transition:background-color 0.2s;" 
                                 onmouseover="this.style.backgroundColor='#f5f5f5';" 
                                 onmouseout="this.style.backgroundColor='#fff';" 
                                 onclick="loadTemplate(${template.id}, '${clinicSlug}')">
                                <strong>${template.name}</strong> 
                                <small style="color:#666;"> (${template.medicines_count} meds, ${template.tests_count} tests)</small>
                                ${template.keyword ? `<br><small style="color:#999;">Keyword: ${template.keyword}</small>` : ''}
                            </div>`;
                        });
                        html += '</div>';
                        templateSuggestions.innerHTML = html;
                        templateSuggestions.style.display = "block";
                    } else {
                        console.log("ℹ️ No templates found");
                        templateSuggestions.innerHTML = '<small style="color:#999;">No templates found</small>';
                        templateSuggestions.style.display = "block";
                    }
                })
                .catch(err => {
                    console.error("❌ Template search fetch error:", err);
                    templateSuggestions.innerHTML = '<small style="color:#f00;">Error loading templates</small>';
                });
            }, 300);
        });
    }

    // Global function to load template
    window.loadTemplate = function(templateId, clinicSlug) {
        console.log("📂 Loading template ID:", templateId, "from clinic:", clinicSlug);
        
        const loadUrl = `/clinic/${clinicSlug}/doctor/templates/${templateId}/load/`;
        console.log("🔗 Loading template from:", loadUrl);
        
        fetch(loadUrl, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            console.log("📥 Template Load Response:", data);
            if (data.medicines || data.tests) {
                console.log(`✅ Template loaded - ${data.medicines?.length || 0} medicines, ${data.tests?.length || 0} tests`);
                
                // Add medicines to prescription
                if (data.medicines) {
                    data.medicines.forEach(med => {
                        console.log("💊 Adding medicine:", med.medicine_name);
                        addMedicineToForm(med);
                    });
                }

                // Add tests to prescription
                if (data.tests) {
                    data.tests.forEach(test => {
                        console.log("🧪 Adding test:", test.test_name);
                        addTestToForm(test);
                    });
                }

                alert(`Template "${data.template_name}" loaded successfully!`);
                templateSearch.value = '';
                templateSuggestions.style.display = 'none';
            }
        })
        .catch(err => {
            console.error("❌ Load template fetch error:", err);
            alert("Error loading template");
        });
    };

    // Helper function to add medicine to form and submit
    function addMedicineToForm(med) {
        console.log("🔧 Adding medicine to form:", med);
        const form = document.querySelector(".medicine-form");
        if (form) {
            // Fill the form fields
            document.querySelector('[name="medicine_name"]').value = med.medicine_name;
            document.querySelector('[name="dosage"]').value = med.dosage;
            document.querySelector('[name="frequency_per_day"]').value = med.frequency_per_day;
            document.querySelector('[name="duration"]').value = med.duration;
            document.querySelector('[name="medicine_type"]').value = med.medicine_type;
            document.querySelector('[name="schedule"]').value = med.schedule;
            document.querySelector('[name="food_instruction"]').value = med.food_instruction;
            document.querySelector('[name="qty"]').value = med.qty;
            document.querySelector('[name="instructions"]').value = med.instructions || '';

            console.log("✓ Form fields populated, submitting...");
            // Auto-submit the form via AJAX
            submitMedicineViaAjax(form);
        } else {
            console.error("❌ Medicine form not found");
        }
    }

    function submitMedicineViaAjax(form) {
        console.log("📤 Submitting medicine via AJAX");
        const formData = new FormData(form);

        fetch("", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            console.log("📥 Add Medicine Response:", data);
            if (data.success) {
                const med = data.medicine;
                console.log("✅ Medicine added - ID:", med.id);
                const row = `
                <tr id="medicine-row-${med.id}">
                    <td>${med.name}</td>
                    <td>${med.type}</td>
                    <td>${med.dosage}</td>
                    <td>${med.frequency_per_day}</td>
                    <td>${med.duration}</td>
                    <td>${med.qty}</td>
                    <td>${med.schedule}</td>
                    <td>${med.food_instruction}</td>
                    <td>
                        <button class="btn btn-sm btn-danger delete-btn"
                                data-id="${med.id}"
                                data-type="medicine">
                        Delete
                        </button>
                    </td>
                </tr>`;

                document.getElementById("medicine-table-body").insertAdjacentHTML("beforeend", row);
                form.reset();
            } else {
                console.error("❌ Failed to add medicine:", data);
            }
        })
        .catch(err => {
            console.error("❌ Add medicine fetch error:", err);
        });
    }

    function addTestToForm(test) {
        console.log("🔧 Adding test to form:", test);
        const form = document.querySelector(".test-form");
        if (form) {
            document.getElementById("test_type_field").value = test.test_type;
            document.getElementById("test_name_field").value = test.test_name;
            
            // Find the datepicker if exists and set to today
            const dateInput = document.querySelector('[name="test_date"]');
            if (dateInput) {
                const today = new Date().toISOString().split('T')[0];
                dateInput.value = today;
            }

            document.querySelector('[name="description"]').value = test.description || '';

            console.log("✓ Test form fields populated, submitting...");
            // Auto-submit form
            submitTestViaAjax(form);
        } else {
            console.error("❌ Test form not found");
        }
    }

    function submitTestViaAjax(form) {
        console.log("📤 Submitting test via AJAX");
        const formData = new FormData(form);

        fetch("", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            console.log("📥 Add Test Response:", data);
            if (data.success) {
                const test = data.test;
                console.log("✅ Test added - ID:", test.id);
                const row = `
                <tr id="test-row-${test.id}">
                    <td>${test.name}</td>
                    <td>${test.type}</td>
                    <td>${test.date}</td>
                    <td>${test.completed ? "Yes" : "Pending"}</td>
                    <td>
                        <button class="btn btn-sm btn-danger delete-btn"
                                data-id="${test.id}"
                                data-type="test">
                        Delete
                        </button>
                    </td>
                </tr>`;

                document.getElementById("test-table-body").insertAdjacentHTML("beforeend", row);
                form.reset();
            } else {
                console.error("❌ Failed to add test:", data);
            }
        })
        .catch(err => {
            console.error("❌ Add test fetch error:", err);
        });
    }

})();

console.log("✅ Prescription Templates Module Initialized");
