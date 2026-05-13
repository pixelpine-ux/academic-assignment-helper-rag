# 🧪 Testing Checklist

## Pre-Test Setup

```bash
# 1. Ensure backend is running
docker-compose up -d

# 2. Start frontend
cd frontend
npm run dev

# 3. Open browser
# Visit: http://localhost:5173
```

---

## ✅ Test 1: Plagiarism Detection

### Steps:
1. [ ] Login to dashboard
2. [ ] Upload 2-3 documents (PDF, DOCX, or TXT)
3. [ ] Hover over a document in sidebar
4. [ ] Verify Shield icon appears
5. [ ] Click Shield icon
6. [ ] Modal should open with plagiarism results
7. [ ] Verify shows:
   - [ ] Filename
   - [ ] Risk level indicator
   - [ ] Hash check result
   - [ ] Vector similarity score
8. [ ] Click "Close" button
9. [ ] Modal should close

### Expected Results:
- ✅ Shield icon visible on hover
- ✅ Modal opens smoothly
- ✅ Results display correctly
- ✅ Color-coded risk indicators
- ✅ No console errors

---

## ✅ Test 2: Assignments Management

### Test 2A: Navigation
1. [ ] From dashboard, click "Assignments" in sidebar
2. [ ] Should navigate to `/assignments`
3. [ ] Click "Back to Dashboard"
4. [ ] Should return to dashboard

### Test 2B: Create Assignment
1. [ ] Go to Assignments page
2. [ ] Click "New Assignment" button
3. [ ] Modal should open
4. [ ] Fill in:
   - [ ] Title: "Test Assignment"
   - [ ] Description: "This is a test"
   - [ ] Due Date: (pick future date)
   - [ ] Status: "Draft"
5. [ ] Click "Create"
6. [ ] Assignment should appear in grid
7. [ ] Verify card shows all info

### Test 2C: Filter Assignments
1. [ ] Create assignments with different statuses
2. [ ] Click "Draft" tab
3. [ ] Should show only draft assignments
4. [ ] Click "Published" tab
5. [ ] Should show only published assignments
6. [ ] Verify count badges update

### Test 2D: Edit Assignment
1. [ ] Hover over assignment card
2. [ ] Edit icon should appear
3. [ ] Click edit icon
4. [ ] Modal opens with existing data
5. [ ] Change title to "Updated Assignment"
6. [ ] Change status to "Published"
7. [ ] Click "Update"
8. [ ] Card should update immediately

### Test 2E: Delete Assignment
1. [ ] Hover over assignment card
2. [ ] Delete icon should appear
3. [ ] Click delete icon
4. [ ] Confirmation dialog appears
5. [ ] Click "OK"
6. [ ] Assignment removed from grid
7. [ ] Success toast appears

### Test 2F: Overdue Detection
1. [ ] Create assignment with past due date
2. [ ] Verify "Overdue" badge appears
3. [ ] Badge should be red/error color

### Expected Results:
- ✅ Navigation works smoothly
- ✅ CRUD operations work
- ✅ Filters work correctly
- ✅ Status badges color-coded
- ✅ Overdue detection works
- ✅ Responsive layout
- ✅ No console errors

---

## ✅ Test 3: Integration Tests

### Test 3A: Chat + Plagiarism
1. [ ] Upload document
2. [ ] Ask question about document
3. [ ] Get response
4. [ ] Check plagiarism on same document
5. [ ] Both features work independently

### Test 3B: Assignments + Documents
1. [ ] Create assignment
2. [ ] Upload document
3. [ ] Both features work independently
4. [ ] No conflicts

### Test 3C: Full Workflow
1. [ ] Create assignment
2. [ ] Upload documents
3. [ ] Ask questions
4. [ ] Check plagiarism
5. [ ] Update assignment status
6. [ ] All features work together

---

## 🐛 Bug Tracking

### Found Issues:
| Issue | Severity | Status | Notes |
|-------|----------|--------|-------|
| | | | |

---

## 📊 Test Results Summary

**Date:** ___________  
**Tester:** ___________

**Plagiarism Detection:**
- [ ] All tests passed
- [ ] Issues found: ___________

**Assignments Management:**
- [ ] All tests passed
- [ ] Issues found: ___________

**Integration:**
- [ ] All tests passed
- [ ] Issues found: ___________

**Overall Status:**
- [ ] ✅ Ready for production
- [ ] ⚠️ Minor issues (non-blocking)
- [ ] ❌ Major issues (blocking)

**Notes:**
_______________________________________
_______________________________________
_______________________________________
