# Supabase Storage Setup Guide

Complete guide for setting up file attachment storage in Supabase.

---

## Prerequisites

- ✅ Supabase project active
- ✅ Admin access to Supabase Dashboard
- ✅ `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

---

## Step 1: Create Storage Bucket

### 1.1 Navigate to Storage

1. Open Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Click **Storage** in left sidebar
4. Click **"Create a new bucket"** button

### 1.2 Configure Bucket

**Bucket Settings:**
```
Name: attachments
Public: ✅ Yes (required for image URLs)
File size limit: 10 MB
Allowed MIME types: Leave empty (we validate in code)
```

Click **"Create bucket"**

---

## Step 2: Set Storage Policies

### 2.1 Allow Public Read Access

This allows image URLs to be publicly accessible.

1. Click on `attachments` bucket
2. Go to **"Policies"** tab
3. Click **"New Policy"**
4. Click **"Get started quickly"**
5. Select **"Enable read access for all users"**

**The policy will be created automatically!**

---

### 2.2 Allow Authenticated Upload

This allows the app to upload files.

**Option A: Using Template (Recommended)**

1. Click **"New Policy"** again
2. Click **"Get started quickly"**
3. Select **"Enable insert access for authenticated users only"**
4. The policy will be created automatically!

**Option B: Custom Policy (Advanced)**

If you need custom policy:

1. Click **"New Policy"**
2. Select **"Create a policy from scratch"**
3. Fill in the fields:

```
Policy name: Allow authenticated uploads
Allowed operations: ✅ INSERT
Target roles: authenticated

USING expression: (leave empty for INSERT)

WITH CHECK expression:
bucket_id = 'attachments'
```

4. Click **"Review"** → **"Save policy"**

---

## Step 3: Verify Configuration

### Test Query in SQL Editor

1. Go to **SQL Editor** in Supabase Dashboard
2. Copy and paste this query (without the backticks):

**Copy this:**
```
SELECT * FROM storage.buckets WHERE name = 'attachments';
```

3. Click **"Run"** or press `Ctrl+Enter`

**Expected Result:**

You should see 1 row with these columns:
```
id          | name        | public | file_size_limit
------------+-------------+--------+----------------
<some-uuid> | attachments | true   | 10485760
```

✅ If you see this, the bucket is configured correctly!

❌ If you get "no rows returned", the bucket wasn't created properly.

---

## Step 4: Get Bucket URL

Your files will be accessible at:

```
https://<project-id>.supabase.co/storage/v1/object/public/attachments/<filename>
```

**Example:**
```
https://seaoujebnhmuaeolhswo.supabase.co/storage/v1/object/public/attachments/article-image-123.jpg
```

---

## File Upload Flow

```
User uploads file in UI
      ↓
File validated (type, size)
      ↓
Uploaded to Supabase Storage
      ↓
Public URL generated
      ↓
URL passed to agent
      ↓
Agent uses in article
```

---

## Supported File Types

**Images:**
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images
- `.webp` - WebP images

**Documents:**
- `.pdf` - PDF documents (text extracted)

**Limits:**
- Max file size: 10MB per file
- Max files per request: 3 files

---

## Troubleshooting

### "Bucket not found" Error

**Cause:** Bucket name mismatch  
**Fix:** Ensure bucket name is exactly `attachments`

### "Permission denied" Error

**Cause:** Missing storage policies  
**Fix:** Re-create policies from Step 2

### Upload fails silently

**Cause:** Invalid `SUPABASE_KEY`  
**Fix:** Verify `.env` has correct service role key

### Files not publicly accessible

**Cause:** Bucket not set to public  
**Fix:** Edit bucket settings → Enable "Public bucket"

---

## Security Best Practices

✅ **Use service role key** for server-side uploads  
✅ **Validate file types** before upload  
✅ **Check file sizes** (10MB limit)  
✅ **Generate unique filenames** to prevent overwrites  
✅ **Enable RLS** for additional security  

❌ **Don't** expose service key in client code  
❌ **Don't** allow unlimited file sizes  
❌ **Don't** skip file type validation  

---

## Verification Checklist

Before proceeding with implementation:

- [ ] Bucket `attachments` created
- [ ] Bucket set to **Public**
- [ ] File size limit: 10MB
- [ ] "Allow public read access" policy added
- [ ] "Allow authenticated uploads" policy added
- [ ] Test query returns bucket info
- [ ] `SUPABASE_KEY` in `.env` is service role key

---

## Next Steps

Once setup is complete:
1. ✅ Storage bucket ready
2. ➡️ Install dependencies (`pdfplumber`, `Pillow`)
3. ➡️ Create `file_handler.py`
4. ➡️ Update Streamlit UI
5. ➡️ Test uploads

---

## Manual Test

After implementation, test with:

1. Upload a small image (< 1MB)
2. Check Supabase Storage → See file listed
3. Copy public URL
4. Open URL in browser → Image displays
5. Success! ✅
