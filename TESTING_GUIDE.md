# Quick Testing Guide - UI Enhancements

## 🎯 How to Test the New Features

Follow these simple steps to test each new feature on your development branch.

---

## ✅ Prerequisites

Make sure you're on the development branch and server is running:

```bash
# Check current branch
git branch

# Should show: * development

# Start the development server
python manage.py runserver
```

Visit: http://localhost:8000/

---

## Feature 1: Sticky Header (2 minutes)

### Test Steps:

1. **Login** to the application
2. **Go to any page** with scrollable content (Dashboard, Employee List, etc.)
3. **Scroll down** the page slowly
4. **Observe**: The navigation bar should stay at the top of the screen

### ✅ Success Criteria:
- Navigation bar remains visible while scrolling
- No content is hidden under the navbar
- All navigation links are clickable while scrolled down
- Works on different screen sizes (resize browser window)

### Screenshot Locations to Check:
- Dashboard (charts and data)
- Employee List (long list)
- Certificate List (long list)

---

## Feature 2: Dark Mode Default (3 minutes)

### Test Steps:

1. **Open Browser DevTools** (F12)
2. **Go to Application/Storage tab** → **Local Storage**
3. **Delete** the 'theme' entry (if it exists)
4. **Refresh the page** (F5)

### ✅ Success Criteria:
- Page loads in **dark mode** by default
- No flash of light theme before dark mode loads
- All text is readable
- All UI elements visible

### Test Theme Toggle:

1. **Click** the sun/moon icon in the navbar
2. **Verify**: Page switches to light mode
3. **Refresh** the page
4. **Verify**: Light mode persists
5. **Click** sun/moon icon again
6. **Verify**: Switches back to dark mode

### Color Check:
- Background: Dark
- Text: Light
- Cards: Dark with subtle borders
- Buttons: Properly colored
- Dropdowns: Dark themed

---

## Feature 3: Admin Role Management (5 minutes)

### Part A: Test as Admin

1. **Login as Admin** account
2. **Go to** Employees page
3. **Click** on any employee (not admin)
4. **Click** "Edit Profile" button
5. **Scroll down** to see "User Role" section

### ✅ Success Criteria (Admin View):
- Yellow warning alert appears saying "Administrator Privilege"
- "User Role" dropdown is visible
- "Admin Only" badge shows next to label
- Dropdown shows current role selected
- Help text explains role differences

### Test Role Change (Employee → Admin):

1. **Select** "Admin" from dropdown
2. **Click** "Save Changes"
3. **Verify**: Success message appears
4. **Verify**: Info message says "User role changed to Admin"
5. **Go back** to employee list
6. **Check**: User now has "Admin" badge

### Test Role Change (Admin → Employee):

1. **Edit the same profile** again
2. **Select** "Employee" from dropdown
3. **Click** "Save Changes"
4. **Verify**: User role changed back to Employee
5. **Check**: "Employee" badge shows

### Part B: Test as Employee

1. **Logout**
2. **Login as Employee** account
3. **Go to** "My Profile" (your own profile)
4. **Click** "Edit Profile"

### ✅ Success Criteria (Employee View):
- **Role field is NOT visible** (should be completely hidden)
- No warning alert about admin privilege
- Can still edit name, department, position, photo
- Cannot see or change role

### Test Security (Advanced):

1. **Open Browser DevTools** → **Console**
2. **Try to manually add role field** (not recommended, just checking)
3. **Submit form** with role field
4. **Verify**: Backend rejects the change
5. **Verify**: Role does not change

---

## 🎨 Visual Appearance Check

### Dark Mode Elements:

| Element | Expected Appearance |
|---------|-------------------|
| Background | Dark gray (#1f2937 or similar) |
| Cards | Slightly lighter dark (#374151) |
| Text | White/light gray |
| Navigation | Dark with shadow |
| Buttons | Proper contrast colors |
| Inputs | Dark with light text |
| Dropdowns | Dark themed |

### Sticky Header:

| Screen Size | Expected Behavior |
|-------------|------------------|
| Desktop (1920px) | Navbar stays at top, no overlap |
| Laptop (1366px) | Navbar stays at top, responsive |
| Tablet (768px) | Navbar stays at top, mobile menu works |
| Mobile (375px) | Navbar stays at top, hamburger menu visible |

---

## 🐛 Common Issues to Check

### Issue 1: Sticky Header

**If navbar scrolls away**:
- Check browser console for errors
- Verify `sticky top-0 z-50` classes applied
- Hard refresh (Ctrl+Shift+R)

**If content hidden under navbar**:
- Check page padding
- Should have `pt-6` class on main content

### Issue 2: Dark Mode

**If loads in light mode**:
- Check localStorage has correct theme
- Check console for JavaScript errors
- Verify both theme scripts are present

**If flashes light before dark**:
- Should not happen (script in `<head>`)
- If it does, clear cache and retry

### Issue 3: Role Management

**If admin can't see role field**:
- Check admin user has `is_admin()` = True
- Check `is_admin` context variable in template
- Check form initialization receives `current_user`

**If employee can see role field**:
- **This is a bug** - check form `__init__` method
- Verify `current_user.is_admin()` check works

**If role change doesn't save**:
- Check form validation errors
- Check browser console
- Verify database permissions

---

## 📊 Test Results Template

Copy this and fill in your results:

```
TESTING RESULTS - UI Enhancements
Date: _______________
Tested by: _______________

Feature 1: Sticky Header
[ ] Navbar stays at top while scrolling
[ ] No content hidden
[ ] Works on mobile
[ ] Works on desktop
Status: PASS / FAIL
Notes: _____________________

Feature 2: Dark Mode Default
[ ] Loads in dark mode by default
[ ] No flash of light theme
[ ] Theme toggle works
[ ] Theme persists after refresh
[ ] All elements readable
Status: PASS / FAIL
Notes: _____________________

Feature 3: Role Management
Admin Tests:
[ ] Role field visible to admin
[ ] Warning alert shows
[ ] Can change Employee → Admin
[ ] Can change Admin → Employee
[ ] Role badge updates

Employee Tests:
[ ] Role field hidden from employee
[ ] Cannot submit role changes
[ ] Other profile edits work normally

Status: PASS / FAIL
Notes: _____________________

Overall Status: PASS / FAIL / NEEDS FIXES
```

---

## 🚀 After Testing

### If All Tests Pass:

1. **Document** any observations
2. **Commit** changes if you made any fixes:
   ```bash
   git add .
   git commit -m "Testing complete - UI enhancements verified"
   git push origin development
   ```

3. **Ready to merge** to main when approved

### If Tests Fail:

1. **Document** the exact issue
2. **Include**:
   - What you did
   - What you expected
   - What actually happened
   - Browser console errors (if any)
   - Screenshots (if helpful)

3. **Report** the issue for fixing

---

## 💡 Testing Tips

1. **Clear cache** between tests (Ctrl+Shift+R)
2. **Use incognito mode** for fresh state
3. **Test in multiple browsers** (Chrome, Firefox, Edge)
4. **Try different screen sizes** (responsive design)
5. **Check mobile view** (device toolbar in DevTools)
6. **Look for console errors** (F12 → Console tab)

---

## 📸 What to Look For

### Sticky Header Success:
![Navbar visible while scrolled down - stays at top]

### Dark Mode Success:
- Dark background immediately on load
- All text readable
- Buttons properly contrasted
- Theme toggle icon changes

### Role Management Success:
**Admin View**:
- Yellow warning box
- Role dropdown visible
- "Admin Only" badge
- Clear help text

**Employee View**:
- No role section at all
- Rest of form works normally

---

## ✅ Quick Test Checklist

**5-Minute Quick Test**:
- [ ] Login
- [ ] Scroll any page → navbar stays
- [ ] Theme is dark by default
- [ ] Toggle theme → works
- [ ] Edit profile as admin → role field shows
- [ ] Edit profile as employee → role field hidden

**Done!** If all checked, features work correctly.

---

*Happy Testing! 🎉*
