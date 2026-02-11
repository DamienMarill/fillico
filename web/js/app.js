/**
 * 🍭 Fillico - Main Application
 * Logique frontend pour l'interface Kawaii
 */

// State
const state = {
  files: [], // Contient {path, name, size, type, status: 'pending'|'processing'|'success'|'error', progress: string}
  selectedFileIndex: null,
  isProcessing: false,
  mascotState: "idle",
  userSetOutputFolder: false,
};

// DOM Elements
const elements = {
  dropZone: document.getElementById("dropZone"),
  fileInput: document.getElementById("fileInput"),
  fileList: document.getElementById("fileList"),
  resultsSection: document.getElementById("resultsSection"),
  resultsList: document.getElementById("resultsList"),
  watermarkText: document.getElementById("watermarkText"),
  opacitySlider: document.getElementById("opacitySlider"),
  opacityValue: document.getElementById("opacityValue"),
  outputFolder: document.getElementById("outputFolder"),
  processBtn: document.getElementById("processBtn"),
  progressSection: document.getElementById("progressSection"),
  progressFill: document.getElementById("progressFill"),
  progressText: document.getElementById("progressText"),
  mascot: document.getElementById("mascot"),
};

// Mascot states - images mapping
const mascotImages = {
  idle: "assets/images/stamp_1.png",
  drag: "assets/images/stamp_2.png",
  processing: "assets/images/stamp_3.png",
  done: "assets/images/stamp_4.png",
};

// ═══════════════════════════════════════════════════════════════
// MASCOT MANAGEMENT
// ═══════════════════════════════════════════════════════════════

function setMascotState(newState) {
  if (state.mascotState === newState) return;

  state.mascotState = newState;
  const mascot = elements.mascot;

  // Remove all state classes
  mascot.classList.remove("idle", "drag", "processing", "done");

  // Add new state class
  mascot.classList.add(newState);

  // Update image
  mascot.src = mascotImages[newState] || mascotImages.idle;
}

// ═══════════════════════════════════════════════════════════════
// DRAG & DROP
// ═══════════════════════════════════════════════════════════════

function initDragDrop() {
  const dropZone = elements.dropZone;

  // Click to select - use Python file picker for real paths
  dropZone.addEventListener("click", async () => {
    if (window.pywebview) {
      try {
        const files = await pywebview.api.select_files();
        if (files && files.length > 0) {
          handleFilesFromPython(files);
        }
      } catch (e) {
        console.error("File selection error:", e);
        showNotification("Erreur lors de la sélection", "error");
      }
    } else {
      // Fallback pour dev sans pywebview
      elements.fileInput.click();
    }
  });

  // File input change (fallback)
  elements.fileInput.addEventListener("change", (e) => {
    // Note: Browser files don't have real paths
    showNotification("Utilisez le clic pour sélectionner avec les vrais chemins", "info");
  });

  // Drag events
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
    setMascotState("drag");
  });

  dropZone.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    setMascotState("idle");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    setMascotState("idle");

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  });
}

// ═══════════════════════════════════════════════════════════════
// FILE HANDLING
// ═══════════════════════════════════════════════════════════════

const SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf"];

function isSupported(file) {
  const ext = "." + file.name.split(".").pop().toLowerCase();
  return SUPPORTED_EXTENSIONS.includes(ext);
}

function getFileIcon(fileName) {
  const ext = fileName.split(".").pop().toLowerCase();
  const icons = {
    png: "🖼️",
    jpg: "🖼️",
    jpeg: "🖼️",
    bmp: "🖼️",
    gif: "🖼️",
    pdf: "📄",
  };
  return icons[ext] || "📁";
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

/**
 * Gère les fichiers venant du sélecteur Python (avec vrais chemins)
 */
async function handleFilesFromPython(filePaths) {
  if (filePaths.length === 0) {
    showNotification("Aucun fichier sélectionné !", "error");
    return;
  }

  // Créer des objets fichier avec les chemins complets et récupérer les tailles
  const newFiles = [];
  for (const path of filePaths) {
    const name = path.split(/[\\/]/).pop();
    let size = 0;
    
    // Récupérer la taille du fichier via Python
    if (window.pywebview) {
      try {
        const info = await pywebview.api.get_file_info(path);
        size = info.size || 0;
      } catch (e) {
        console.warn("Could not get file info:", e);
      }
    }
    
    newFiles.push({
      path: path,
      name: name,
      size: size,
      type: getFileType(name),
      status: "pending", // pending, processing, success, error
      progress: "",
    });
  }

  // Add to state
  state.files.push(...newFiles);

  // Auto-set output folder from first file's directory
  if (!state.userSetOutputFolder && newFiles.length > 0) {
    try {
      const folder = await pywebview.api.get_file_directory(newFiles[0].path);
      if (folder) {
        elements.outputFolder.value = folder;
      }
    } catch (e) {
      console.warn("Could not get file directory:", e);
    }
  }

  // Update UI
  updateFileList();
  updateProcessButton();

  showNotification(`${newFiles.length} fichier(s) ajouté(s) !`, "success");
}

function getFileType(fileName) {
  const ext = fileName.split(".").pop().toLowerCase();
  const types = {
    png: "image/png",
    jpg: "image/jpeg",
    jpeg: "image/jpeg",
    bmp: "image/bmp",
    gif: "image/gif",
    pdf: "application/pdf",
  };
  return types[ext] || "application/octet-stream";
}

async function handleFiles(files) {
  const supportedFiles = files.filter(isSupported);

  if (supportedFiles.length === 0) {
    showNotification("Aucun fichier supporté trouvé !", "error");
    return;
  }

  // Les fichiers browser n'ont pas de path réel - on doit les uploader vers Python
  if (window.pywebview) {
    showNotification("Upload des fichiers...", "info");
    
    for (const file of supportedFiles) {
      try {
        // Lire le fichier en base64
        const base64 = await readFileAsBase64(file);
        
        // Envoyer à Python pour sauvegarder dans un dossier temporaire
        const result = await pywebview.api.upload_file(file.name, base64);
        
        if (result.success) {
          // Ajouter le fichier avec le vrai chemin retourné par Python
          state.files.push({
            path: result.path,
            name: file.name,
            size: file.size,
            type: file.type,
            status: "pending",
            progress: "",
          });
        } else {
          showNotification(`Erreur upload ${file.name}: ${result.error}`, "error");
        }
      } catch (e) {
        console.error("Upload error:", e);
        showNotification(`Erreur upload ${file.name}`, "error");
      }
    }
    
    // Update UI
    updateFileList();
    updateProcessButton();
    
    showNotification(`${state.files.length} fichier(s) prêt(s) !`, "success");
  } else {
    // Mode dev sans pywebview - juste afficher les fichiers sans path
    state.files.push(...supportedFiles.map(f => ({
      path: null,
      name: f.name,
      size: f.size,
      type: f.type,
      status: "pending",
      progress: "",
    })));
    updateFileList();
    updateProcessButton();
    showNotification(`${supportedFiles.length} fichier(s) ajouté(s) !`, "success");
  }
}

/**
 * Lit un fichier en base64
 */
function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // Retirer le préfixe data:xxx;base64,
      const base64 = reader.result.split(",")[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Icônes de statut pour la progression
 */
function getStatusIcon(status) {
  const icons = {
    pending: "⏳",
    processing: "⚙️",
    success: "✅",
    error: "❌",
  };
  return icons[status] || "📄";
}

function updateFileList() {
  const fileList = elements.fileList;

  if (state.files.length === 0) {
    fileList.classList.add("hidden");
    return;
  }

  fileList.classList.remove("hidden");
  fileList.innerHTML = "";

  state.files.forEach((file, index) => {
    const item = document.createElement("div");
    // Désactiver l'animation pendant le traitement pour éviter le clignotement
    const animClass = state.isProcessing ? "" : "slide-in";
    item.className = `file-item ${animClass} ${file.status || "pending"}`;
    if (!state.isProcessing) {
      item.style.animationDelay = `${index * 50}ms`;
    }
    item.dataset.index = index;
    
    // Pendant le traitement, on affiche le statut au lieu du bouton supprimer
    const isProcessing = state.isProcessing;
    const statusIcon = getStatusIcon(file.status);
    const progressInfo = file.progress ? ` - ${file.progress}` : "";

    item.innerHTML = `
      <span class="file-item-status" title="${file.status}">${statusIcon}</span>
      <span class="file-item-icon">${getFileIcon(file.name)}</span>
      <span class="file-item-name">${file.name}${progressInfo}</span>
      <span class="file-item-size">${formatFileSize(file.size)}</span>
      ${!isProcessing ? `<button class="file-item-remove" data-index="${index}" title="Retirer">✕</button>` : ""}
    `;

    // Click to select (juste pour le style visuel)
    item.addEventListener("click", (e) => {
      if (!e.target.classList.contains("file-item-remove")) {
        state.selectedFileIndex = index;
        // Update UI selection
        elements.fileList.querySelectorAll(".file-item").forEach((el, i) => {
          el.style.borderColor = i === index ? "var(--bubblegum-pink)" : "var(--magic-berry-light)";
        });
      }
    });

    fileList.appendChild(item);
  });

  // Add remove listeners
  fileList.querySelectorAll(".file-item-remove").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      removeFile(parseInt(btn.dataset.index));
    });
  });
}



function removeFile(index) {
  state.files.splice(index, 1);

  // Adjust selection
  if (state.selectedFileIndex === index) {
    state.selectedFileIndex = null;
  } else if (state.selectedFileIndex > index) {
    state.selectedFileIndex--;
  }

  updateFileList();
  updateProcessButton();
}

function updateProcessButton() {
  elements.processBtn.disabled = state.files.length === 0 || state.isProcessing;
}


// ═══════════════════════════════════════════════════════════════
// PROCESSING (Eel Integration Point)
// ═══════════════════════════════════════════════════════════════

async function processFiles() {
  if (state.files.length === 0 || state.isProcessing) return;

  state.isProcessing = true;
  setMascotState("processing");
  updateProcessButton();
  
  // Réinitialiser les statuts
  state.files.forEach(f => {
    f.status = "pending";
    f.progress = "";
  });
  updateFileList();

  // Masquer les résultats précédents (la progression est maintenant dans la liste des fichiers)
  elements.progressSection.classList.add("hidden");
  elements.resultsSection.classList.add("hidden");
  elements.resultsList.innerHTML = "";

  const results = [];
  const total = state.files.length;

  for (let i = 0; i < total; i++) {
    const file = state.files[i];

    // Marquer le fichier en cours de traitement
    file.status = "processing";
    file.progress = "En cours...";
    updateFileList();

    try {
      // Call Eel function (or simulate)
      let result;
      if (window.pywebview) {
        // Vérifier que le fichier a un chemin réel (sélectionné via Python, pas drag&drop navigateur)
        if (!file.path) {
          throw new Error("Fichier sans chemin réel. Utilisez le sélecteur de fichiers.");
        }
        // Appel pywebview
        result = await pywebview.api.process_file(
          file.path,
          elements.watermarkText.value,
          parseInt(elements.opacitySlider.value) / 100,
          elements.outputFolder.value || null,
        );
      } else {
        // Simulation for testing
        await sleep(500);
        result = {
          success: true,
          input: file.name,
          output: file.name.replace(/(\.[^.]+)$/, "_watermarked$1"),
        };
      }

      // Mettre à jour le statut du fichier
      file.status = result.success ? "success" : "error";
      file.progress = result.success ? "Terminé" : result.error || "Erreur";
      updateFileList();
      
      results.push(result);
    } catch (error) {
      // Erreur: mettre à jour le statut
      file.status = "error";
      file.progress = error.message || "Erreur inconnue";
      updateFileList();
      
      results.push({
        success: false,
        input: file.name,
        error: error.message || "Erreur inconnue",
      });
    }
  }

  // Complete
  state.isProcessing = false;
  setMascotState("done");
  updateFileList(); // Rafraîchir une dernière fois pour montrer les boutons de suppression
  showResults(results);
  updateProcessButton();

  // Reset mascot after delay
  setTimeout(() => {
    if (!state.isProcessing) {
      setMascotState("idle");
    }
  }, 3000);
}

function showResults(results) {
  elements.progressSection.classList.add("hidden");
  elements.resultsSection.classList.remove("hidden");
  elements.resultsList.innerHTML = "";

  const successCount = results.filter((r) => r.success).length;
  const totalCount = results.length;

  results.forEach((result, index) => {
    const item = document.createElement("div");
    item.className = `result-item ${result.success ? "success" : "error"} slide-in`;
    item.style.animationDelay = `${index * 100}ms`;

    item.innerHTML = `
      <span class="result-icon">${result.success ? "✅" : "❌"}</span>
      <div style="flex: 1;">
        <span style="font-weight: 600;">${result.input}</span>
        ${
          result.success
            ? `<span style="display: block; font-size: 0.875rem; color: var(--minty-fresh);">
               → ${result.output}
             </span>`
            : `<span style="display: block; font-size: 0.875rem; color: var(--bubblegum-pink);">
               ${result.error}
             </span>`
        }
      </div>
    `;

    elements.resultsList.appendChild(item);
  });

  // Show notification
  if (successCount === totalCount) {
    showNotification(
      `${totalCount} fichier(s) traité(s) avec succès ! ✨`,
      "success",
    );
  } else {
    showNotification(
      `${successCount}/${totalCount} fichier(s) traité(s)`,
      successCount > 0 ? "warning" : "error",
    );
  }

  // Clear files after processing
  state.files = [];
  state.selectedFileIndex = null;
  updateFileList();
}

// ═══════════════════════════════════════════════════════════════
// NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════

function showNotification(message, type = "info") {
  // Create notification
  const notification = document.createElement("div");
  notification.className = "notification fade-in";
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    border-radius: 16px;
    font-weight: 600;
    z-index: 1000;
    backdrop-filter: blur(10px);
    animation: slideIn 0.3s ease;
  `;

  const colors = {
    success: {
      bg: "rgba(52, 211, 153, 0.9)",
      text: "white",
    },
    error: {
      bg: "rgba(244, 114, 182, 0.9)",
      text: "white",
    },
    warning: {
      bg: "rgba(251, 191, 36, 0.9)",
      text: "#4c1d95",
    },
    info: {
      bg: "rgba(167, 139, 250, 0.9)",
      text: "white",
    },
  };

  const color = colors[type] || colors.info;
  notification.style.background = color.bg;
  notification.style.color = color.text;
  notification.textContent = message;

  document.body.appendChild(notification);

  // Remove after delay
  setTimeout(() => {
    notification.style.animation = "fadeOut 0.3s ease forwards";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// ═══════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ═══════════════════════════════════════════════════════════════
// OPACITY SLIDER
// ═══════════════════════════════════════════════════════════════

function initOpacitySlider() {
  elements.opacitySlider.addEventListener("input", (e) => {
    elements.opacityValue.textContent = e.target.value;
  });
}

// ═══════════════════════════════════════════════════════════════
// OUTPUT FOLDER PICKER
// ═══════════════════════════════════════════════════════════════

function initOutputFolderPicker() {
  const outputFolderInput = elements.outputFolder;
  const browseBtn = document.getElementById("browseOutputBtn");
  
  if (browseBtn) {
    browseBtn.addEventListener("click", async () => {
      if (window.pywebview) {
        try {
          const folder = await pywebview.api.select_output_folder(
            outputFolderInput.value || null
          );
          if (folder) {
            outputFolderInput.value = folder;
            state.userSetOutputFolder = true;
            showNotification("Dossier de destination défini !", "success");
          }
        } catch (e) {
          console.error("Folder selection error:", e);
          showNotification("Erreur lors de la sélection du dossier", "error");
        }
      } else {
        // Fallback pour le dev sans pywebview
        showNotification("Sélection de dossier disponible uniquement dans l'app", "info");
      }
    });
  }

  // Mark as user-set if they manually type in the field
  outputFolderInput.addEventListener("input", () => {
    state.userSetOutputFolder = true;
  });
}

// ═══════════════════════════════════════════════════════════════
// PROCESS BUTTON
// ═══════════════════════════════════════════════════════════════

function initProcessButton() {
  elements.processBtn.addEventListener("click", processFiles);
}

// ═══════════════════════════════════════════════════════════════
// CALLBACKS (appelés par Python via evaluate_js)
// ═══════════════════════════════════════════════════════════════

/**
 * Callback appelé par Python pendant le traitement PDF pour mettre à jour la progression.
 * Fonction globale car invoquée via pywebview evaluate_js().
 */
function onPdfProgress(filePath, currentPage, totalPages) {
  // Trouver le fichier correspondant et mettre à jour son progress
  const file = state.files.find(f => f.path === filePath);
  if (file) {
    file.progress = `${currentPage}/${totalPages} pages`;
    updateFileList();
  }
}

// ═══════════════════════════════════════════════════════════════
// LOGO BOUNCE
// ═══════════════════════════════════════════════════════════════

function initLogoBounce() {
  const logo = document.querySelector('.app-logo img');
  if (logo) {
    logo.classList.add('clickable-bounce');
    
    logo.addEventListener('click', () => {
      // Reset animation si déjà en cours
      logo.classList.remove('bouncing');
      void logo.offsetWidth; // Force reflow
      logo.classList.add('bouncing');
      
      // Retirer la classe après l'animation
      setTimeout(() => {
        logo.classList.remove('bouncing');
      }, 800);
    });
  }
}

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════

async function init() {
  initDragDrop();
  initOpacitySlider();
  initOutputFolderPicker();
  initProcessButton();
  
  // Init Background Assets
  if (window.bgAssets) {
    window.bgAssets.init();
  }

  // Init Logo Bounce
  initLogoBounce();

  // Définir le dossier de sortie par défaut (home directory)
  if (window.pywebview) {
    try {
      const defaultFolder = await pywebview.api.get_default_output_folder();
      if (defaultFolder) {
        elements.outputFolder.value = defaultFolder;
      }
    } catch (e) {
      console.warn("Could not get default output folder:", e);
    }

    // Récupérer et afficher la version dans le titre de la fenêtre
    try {
      const version = await pywebview.api.get_app_version();
      if (version) {
        document.title = `Fillico v${version} - 🍭 Filigraner Illico!`;
      }
    } catch (e) {
      console.warn("Could not get app version:", e);
    }
  }

  console.log("🍭 Fillico initialized!");
}

// Start app
document.addEventListener("DOMContentLoaded", init);
