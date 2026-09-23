import gradio as gr
import requests


# =========================================================
# تنظیمات
# =========================================================

N8N_WEBHOOK_URL = "https://kianaz.app.n8n.cloud/webhook/product-description"


# =========================================================
# تابع کمکی برای خروجی خالی
# =========================================================

def empty_outputs(message):
    return (
        message,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        {}
    )


# =========================================================
# تبدیل پاسخ n8n به خروجی‌های Gradio
# =========================================================

def product_to_outputs(data):

    input_validation = data.get(
        "input_validation",
        {}
    ) or {}

    status = input_validation.get(
        "status",
        ""
    )

    # -----------------------------------------------------
    # ورودی ناقص
    # -----------------------------------------------------

    if status == "incomplete":

        missing = input_validation.get(
            "missing_fields",
            []
        )

        if missing:
            missing_text = "، ".join(
                str(item)
                for item in missing
            )
        else:
            missing_text = "اطلاعات ضروری محصول"

        return (
            "⚠️ اطلاعات محصول ناقص است.\n\n"
            f"موارد موردنیاز: {missing_text}",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            {}
        )

    # -----------------------------------------------------
    # وضعیت نامشخص
    # -----------------------------------------------------

    if status != "complete":

        return (
            "⚠️ وضعیت اطلاعات محصول از طرف n8n مشخص نیست.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            {}
        )

    # =====================================================
    # دریافت محصول
    # =====================================================

    product = data.get(
        "product",
        {}
    ) or {}

    title = product.get(
        "title",
        ""
    )

    short_description = product.get(
        "short_description",
        ""
    )

    description = product.get(
        "description",
        ""
    )

    key_features = product.get(
        "key_features",
        []
    )

    meta_title = product.get(
        "meta_title",
        ""
    )

    meta_description = product.get(
        "meta_description",
        ""
    )

    url = product.get(
        "url",
        ""
    )

    # =====================================================
    # وضعیت SEO
    # =====================================================

    seo_validation = data.get(
        "seo_validation",
        {}
    ) or {}

    seo_status = seo_validation.get(
        "status",
        ""
    )

    if seo_status == "passed":

        seo_text = "✓ SEO PASSED"

    elif seo_status == "failed":

        failed_checks = seo_validation.get(
            "failed_checks",
            []
        )

        if failed_checks:

            failed_text = "، ".join(
                str(item)
                for item in failed_checks
            )

            seo_text = (
                "⚠️ SEO نیاز به بررسی دارد\n\n"
                f"موارد نیازمند اصلاح: {failed_text}"
            )

        else:

            seo_text = (
                "⚠️ SEO نیاز به بررسی دارد"
            )

    else:

        seo_text = (
            "⚠️ وضعیت SEO نامشخص است"
        )

    # =====================================================
    # ویژگی‌های کلیدی
    # =====================================================

    if isinstance(key_features, list):

        if key_features:

            features_text = "\n".join(
                f"• {item}"
                for item in key_features
            )

        else:

            features_text = (
                "ویژگی مشخصی برای محصول ثبت نشده است."
            )

    else:

        features_text = str(key_features)

    # =====================================================
    # خروجی
    # =====================================================

    return (
        seo_text,
        title,
        short_description,
        description,
        features_text,
        meta_title,
        meta_description,
        url,
        product
    )


# =========================================================
# تولید محصول
# =========================================================

def generate_product(
    product_name,
    category,
    features,
    target_audience,
    tone
):

    # -----------------------------------------------------
    # اعتبارسنجی فیلدهای ضروری
    # -----------------------------------------------------

    if not product_name or not product_name.strip():

        return empty_outputs(
            "⚠️ نام محصول وارد نشده است."
        )

    if not category or not category.strip():

        return empty_outputs(
            "⚠️ دسته‌بندی محصول وارد نشده است."
        )

    if not tone or not tone.strip():

        return empty_outputs(
            "⚠️ لطفاً لحن محتوا را انتخاب کنید."
        )

    # -----------------------------------------------------
    # Payload
    # -----------------------------------------------------

    payload = {

        "product_name": product_name.strip(),

        "category": category.strip(),

        # اختیاری
        "features": (
            features.strip()
            if features
            else ""
        ),

        # اختیاری
        "target_audience": (
            target_audience.strip()
            if target_audience
            else ""
        ),

        "tone": tone.strip()
    }

    # -----------------------------------------------------
    # ارسال به n8n
    # -----------------------------------------------------

    try:

        response = requests.post(

            N8N_WEBHOOK_URL,

            json=payload,

            timeout=120
        )

        # -------------------------------------------------
        # بررسی HTTP
        # -------------------------------------------------

        if response.status_code != 200:

            error_detail = response.text.strip()

            if len(error_detail) > 500:

                error_detail = (
                    error_detail[:500]
                    + "..."
                )

            return empty_outputs(

                f"❌ خطا در ارتباط با سیستم: "
                f"{response.status_code}\n\n"
                f"{error_detail}"
            )

        # -------------------------------------------------
        # تبدیل پاسخ به JSON
        # -------------------------------------------------

        try:

            data = response.json()

        except ValueError:

            return empty_outputs(
                "❌ پاسخ دریافت‌شده از n8n معتبر نیست."
            )

    except requests.exceptions.Timeout:

        return empty_outputs(
            "⏳ زمان پاسخ‌گویی سیستم تمام شد. "
            "دوباره تلاش کنید."
        )

    except requests.exceptions.ConnectionError:

        return empty_outputs(
            "❌ اتصال به n8n برقرار نشد.\n\n"
            "Webhook یا اتصال اینترنت را بررسی کنید."
        )

    except Exception as e:

        return empty_outputs(
            f"❌ خطا در اتصال به سیستم:\n\n{str(e)}"
        )

    # -----------------------------------------------------
    # تبدیل پاسخ
    # -----------------------------------------------------

    return product_to_outputs(data)


# =========================================================
# ویرایش هوشمند محصول
# =========================================================

def edit_product(
    instruction,
    current_product
):

    # -----------------------------------------------------
    # بررسی وجود محصول
    # -----------------------------------------------------

    if (
        not current_product
        or not isinstance(current_product, dict)
    ):

        return (
            "⚠️ ابتدا یک محصول تولید کنید.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            {}
        )

    # -----------------------------------------------------
    # بررسی دستور
    # -----------------------------------------------------

    if (
        not instruction
        or not instruction.strip()
    ):

        return (
            "⚠️ لطفاً دستور ویرایش را وارد کنید.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            current_product
        )

    # -----------------------------------------------------
    # Payload ویرایش
    # -----------------------------------------------------

    payload = {

        "action": "edit",

        "product": current_product,

        "instruction": instruction.strip()
    }

    # -----------------------------------------------------
    # ارسال به n8n
    # -----------------------------------------------------

    try:

        response = requests.post(

            N8N_WEBHOOK_URL,

            json=payload,

            timeout=120
        )

        # -------------------------------------------------
        # بررسی HTTP
        # -------------------------------------------------

        if response.status_code != 200:

            error_detail = response.text.strip()

            if len(error_detail) > 500:

                error_detail = (
                    error_detail[:500]
                    + "..."
                )

            return (
                f"❌ خطا در ویرایش محصول: "
                f"{response.status_code}\n\n"
                f"{error_detail}",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                current_product
            )

        # -------------------------------------------------
        # JSON
        # -------------------------------------------------

        try:

            data = response.json()

        except ValueError:

            return (
                "❌ پاسخ دریافت‌شده از n8n معتبر نیست.",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                current_product
            )

    except requests.exceptions.Timeout:

        return (
            "⏳ زمان پاسخ‌گویی سیستم تمام شد. "
            "دوباره تلاش کنید.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            current_product
        )

    except requests.exceptions.ConnectionError:

        return (
            "❌ اتصال به n8n برقرار نشد.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            current_product
        )

    except Exception as e:

        return (
            f"❌ خطا در ویرایش محصول:\n\n{str(e)}",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            current_product
        )

    # -----------------------------------------------------
    # تبدیل پاسخ جدید
    # -----------------------------------------------------

    return product_to_outputs(data)


# =========================================================
# CSS
# =========================================================

css = """

@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Vazirmatn', sans-serif !important;
    box-sizing: border-box !important;
}

body {
    margin: 0 !important;

    background:
        radial-gradient(
            circle at top right,
            rgba(254, 150, 119, 0.12),
            transparent 30%
        ),
        #41436A !important;

    color: #FFFFFF !important;
}

.gradio-container {
    max-width: 1050px !important;

    margin: auto !important;

    padding: 35px 22px 25px !important;

    background: transparent !important;

    direction: rtl !important;

    color: #FFFFFF !important;
}

.gradio-container p,
.gradio-container h1,
.gradio-container h2,
.gradio-container h3 {
    color: #FFFFFF !important;
}


/* ========================================================
   HERO
   ======================================================== */

.hero {
    text-align: center !important;

    padding: 25px 20px 35px !important;
}

.hero-title {
    font-size: 38px !important;

    font-weight: 800 !important;

    color: #FFFFFF !important;

    -webkit-text-fill-color: #FFFFFF !important;

    margin-bottom: 12px !important;
}

.hero-subtitle {
    font-size: 16px !important;

    line-height: 2 !important;

    color: #FFFFFF !important;

    opacity: 0.9 !important;
}


/* ========================================================
   CARDS
   ======================================================== */

.luxury-card,
.output-card {

    background: #41436A !important;

    border: 1px solid
        rgba(254, 150, 119, 0.28) !important;

    border-radius: 22px !important;

    padding: 28px !important;

    margin-bottom: 22px !important;

    box-shadow:
        0 12px 35px
        rgba(0, 0, 0, 0.18) !important;
}


/* ========================================================
   SECTION HEADER
   ======================================================== */

.section-header {

    text-align: center !important;

    color: #FFFFFF !important;

    font-size: 18px !important;

    font-weight: 700 !important;

    margin-bottom: 22px !important;
}

.section-header::after {

    content: "";

    display: block;

    width: 55px;

    height: 3px;

    margin: 10px auto 0;

    background: #FE9677 !important;

    border-radius: 10px;
}


/* ========================================================
   LABELS
   ======================================================== */

.luxury-card label,
.luxury-card label *,
.luxury-card .label-wrap,
.luxury-card .label-wrap *,
.luxury-card .gr-form label,
.luxury-card .gr-form label *,
.luxury-card .gr-form .label-wrap,
.luxury-card .gr-form .label-wrap * {

    color: #FE9677 !important;

    -webkit-text-fill-color: #FE9677 !important;

    text-align: center !important;

    font-weight: 500 !important;
}


/* ========================================================
   INFO TEXT
   ======================================================== */

.luxury-card .info,
.luxury-card .info *,
.luxury-card .gr-info,
.luxury-card .gr-info *,
.luxury-card small {

    color: rgba(255, 255, 255, 0.75) !important;

    -webkit-text-fill-color:
        rgba(255, 255, 255, 0.75) !important;

    text-align: center !important;

    width: 100% !important;

    display: block !important;
}


/* ========================================================
   OUTPUT LABELS
   ======================================================== */

.output-card label,
.output-card label *,
.output-card .label-wrap,
.output-card .label-wrap *,
.output-card .gr-form label,
.output-card .gr-form label * {

    color: #FE9677 !important;

    -webkit-text-fill-color: #FE9677 !important;

    text-align: center !important;

    font-weight: 600 !important;
}


/* ========================================================
   INPUTS
   ======================================================== */

.luxury-card textarea,
.luxury-card input {

    background: #303252 !important;

    color: #FFFFFF !important;

    border: 1px solid
        rgba(254, 150, 119, 0.28) !important;

    border-radius: 14px !important;

    text-align: center !important;

    -webkit-text-fill-color: #FFFFFF !important;
}

.luxury-card textarea::placeholder,
.luxury-card input::placeholder {

    color:
        rgba(255, 255, 255, 0.55) !important;
}


/* ========================================================
   INPUT FOCUS
   ======================================================== */

.luxury-card textarea:focus,
.luxury-card input:focus {

    border-color: #FE9677 !important;

    box-shadow:
        0 0 0 2px
        rgba(254, 150, 119, 0.15) !important;
}


/* ========================================================
   DROPDOWN
   ======================================================== */

.luxury-card .gr-dropdown {

    background: #303252 !important;

    border: 1px solid
        rgba(254, 150, 119, 0.28) !important;

    border-radius: 14px !important;
}

.luxury-card .gr-dropdown input {

    background: transparent !important;

    color: #FFFFFF !important;

    -webkit-text-fill-color: #FFFFFF !important;
}


/* ========================================================
   OUTPUT BOXES
   ======================================================== */

.output-card textarea,
.output-card input {

    background: #303252 !important;

    color: #FFFFFF !important;

    -webkit-text-fill-color: #FFFFFF !important;

    border: 1px solid
        rgba(254, 150, 119, 0.30) !important;

    border-radius: 14px !important;

    text-align: right !important;

    line-height: 2 !important;
}


/* ========================================================
   STATUS BOX
   ======================================================== */

.status-box textarea {

    background: #303252 !important;

    color: #FFFFFF !important;

    -webkit-text-fill-color: #FFFFFF !important;

    border: 1px solid #FE9677 !important;

    border-radius: 14px !important;

    font-weight: 700 !important;

    text-align: center !important;
}


/* ========================================================
   URL
   ======================================================== */

.url-output textarea,
.url-output input {

    background: #303252 !important;

    color: #FFFFFF !important;

    -webkit-text-fill-color: #FFFFFF !important;

    direction: ltr !important;

    text-align: center !important;
}


/* ========================================================
   GENERATE BUTTON
   ======================================================== */

.generate-button {

    width: 100% !important;

    min-height: 58px !important;

    background: #FE9677 !important;

    color: #FFFFFF !important;

    -webkit-text-fill-color: #FFFFFF !important;

    border: none !important;

    border-radius: 15px !important;

    font-size: 17px !important;

    font-weight: 700 !important;

    margin-top: 10px !important;

    box-shadow:
        0 8px 22px
        rgba(254, 150, 119, 0.22) !important;

    transition: all 0.2s ease !important;
}

.generate-button:hover {

    background: #FE9677 !important;

    color: #FFFFFF !important;

    transform: translateY(-2px) !important;

    box-shadow:
        0 12px 28px
        rgba(254, 150, 119, 0.32) !important;
}


/* ========================================================
   EDIT BUTTON
   ======================================================== */

.edit-button {

    width: 100% !important;

    min-height: 54px !important;

    background: transparent !important;

    color: #FE9677 !important;

    -webkit-text-fill-color: #FE9677 !important;

    border: 1px solid #FE9677 !important;

    border-radius: 15px !important;

    font-size: 16px !important;

    font-weight: 700 !important;

    margin-top: 10px !important;

    transition: all 0.2s ease !important;
}

.edit-button:hover {

    background:
        rgba(254, 150, 119, 0.12) !important;

    transform: translateY(-2px) !important;
}


/* ========================================================
   EDIT HELP
   ======================================================== */

.edit-help {

    color:
        rgba(255, 255, 255, 0.78) !important;

    line-height: 2 !important;

    text-align: center !important;

    margin-bottom: 15px !important;
}


/* ========================================================
   DIVIDER
   ======================================================== */

.luxury-divider {

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            #FE9677,
            transparent
        );

    margin: 25px 0;
}


/* ========================================================
   FOOTER
   ======================================================== */

.footer {

    text-align: center !important;

    color: #FFFFFF !important;

    opacity: 0.7 !important;

    font-size: 12px !important;

    padding: 20px 0 5px !important;
}


/* ========================================================
   MOBILE
   ======================================================== */

@media (max-width: 700px) {

    .gradio-container {

        padding: 20px 14px !important;
    }

    .hero-title {

        font-size: 28px !important;
    }

    .hero-subtitle {

        font-size: 14px !important;
    }

    .luxury-card,
    .output-card {

        padding: 20px !important;
    }
}

"""


# =========================================================
# UI
# =========================================================

with gr.Blocks(
    css=css,
    title="AI Product Intelligence"
) as demo:

    # محصول فعلی در حافظه همین session نگهداری می‌شود
    current_product = gr.State({})


    # =====================================================
    # HERO
    # =====================================================

    gr.HTML("""
    <div class="hero">

        <div class="hero-title">
            AI Product Intelligence
        </div>

        <div class="hero-subtitle">
            تولید هوشمند توضیحات محصول، تحقیق محصول و اعتبارسنجی SEO
        </div>

    </div>
    """)


    # =====================================================
    # INPUT
    # =====================================================

    with gr.Column(
        elem_classes="luxury-card"
    ):

        gr.HTML("""
        <div class="section-header">
            اطلاعات محصول
        </div>
        """)

        product_name = gr.Textbox(
            label="نام محصول",
            placeholder="مثلاً کرم مرطوب‌کننده پوست خشک",
            lines=1
        )

        category = gr.Textbox(
            label="دسته‌بندی",
            placeholder="مثلاً مراقبت از پوست",
            lines=1
        )

        features = gr.Textbox(
            label="ویژگی‌های محصول (اختیاری)",
            placeholder=(
                "ویژگی‌های اصلی محصول را وارد کنید "
                "یا خالی بگذارید تا سیستم تحقیق محصول انجام دهد..."
            ),
            lines=4
        )

        target_audience = gr.Textbox(
            label="مخاطب هدف (اختیاری)",
            placeholder=(
                "در صورت نیاز، مثلاً افراد دارای پوست خشک"
            ),
            lines=2
        )

        tone = gr.Dropdown(
            choices=[
                "حرفه‌ای و رسمی",
                "فروشگاهی و متقاعدکننده",
                "دوستانه و صمیمی",
                "مینیمال و مستقیم",
                "لوکس و پریمیوم",
                "تخصصی و فنی"
            ],

            value="حرفه‌ای و رسمی",

            label="لحن محتوا",

            info=(
                "سبک نوشتار محتوا براساس انتخاب شما تغییر می‌کند"
            ),

            interactive=True
        )

        generate_btn = gr.Button(
            "تولید محتوای محصول",
            elem_classes="generate-button"
        )


    # =====================================================
    # DIVIDER
    # =====================================================

    gr.HTML("""
    <div class="luxury-divider"></div>
    """)


    # =====================================================
    # SEO STATUS
    # =====================================================

    with gr.Column(
        elem_classes="output-card"
    ):

        gr.HTML("""
        <div class="section-header">
            نتیجه بررسی
        </div>
        """)

        seo_status = gr.Textbox(
            label="وضعیت SEO",
            lines=2,
            interactive=False,
            elem_classes="status-box"
        )


    # =====================================================
    # CONTENT
    # =====================================================

    with gr.Column(
        elem_classes="output-card"
    ):

        gr.HTML("""
        <div class="section-header">
            محتوای تولیدشده
        </div>
        """)

        title = gr.Textbox(
            label="عنوان محصول",
            lines=2,
            interactive=False
        )

        short_description = gr.Textbox(
            label="معرفی کوتاه",
            lines=3,
            interactive=False
        )

        description = gr.Textbox(
            label="توضیحات کامل",
            lines=10,
            interactive=False
        )

        key_features = gr.Textbox(
            label="ویژگی‌های کلیدی",
            lines=5,
            interactive=False
        )


    # =====================================================
    # SEO OUTPUT
    # =====================================================

    with gr.Column(
        elem_classes="output-card"
    ):

        gr.HTML("""
        <div class="section-header">
            اطلاعات SEO
        </div>
        """)

        meta_title = gr.Textbox(
            label="Meta Title",
            lines=2,
            interactive=False
        )

        meta_description = gr.Textbox(
            label="Meta Description",
            lines=4,
            interactive=False
        )

        url = gr.Textbox(
            label="URL",
            lines=1,
            interactive=False,
            elem_classes="url-output"
        )


    # =====================================================
    # SMART EDIT
    # =====================================================

    gr.HTML("""
    <div class="luxury-divider"></div>
    """)

    with gr.Column(
        elem_classes="luxury-card"
    ):

        gr.HTML("""
        <div class="section-header">
            ویرایش هوشمند محصول
        </div>

        <div class="edit-help">
            دستور تغییر موردنظر را بنویسید؛ سیستم فقط همان تغییر را
            روی محتوای فعلی اعمال می‌کند.
            <br>
            مثال:
            «یک پاراگراف درباره نحوه استفاده از محصول به توضیحات اضافه کن»
        </div>
        """)

        edit_instruction = gr.Textbox(
            label="دستور ویرایش",
            placeholder=(
                "مثلاً: لحن توضیحات را کمی فروشگاهی‌تر کن "
                "یا یک پاراگراف درباره نحوه استفاده اضافه کن..."
            ),
            lines=4
        )

        edit_btn = gr.Button(
            "اعمال تغییر روی محتوای فعلی",
            elem_classes="edit-button"
        )


    # =====================================================
    # FOOTER
    # =====================================================

    gr.HTML("""
    <div class="footer">
        AI-powered product research, content & SEO workflow
    </div>
    """)


    # =====================================================
    # GENERATE EVENT
    # =====================================================

    generate_btn.click(

        fn=generate_product,

        inputs=[
            product_name,
            category,
            features,
            target_audience,
            tone
        ],

        outputs=[
            seo_status,
            title,
            short_description,
            description,
            key_features,
            meta_title,
            meta_description,
            url,
            current_product
        ]
    )


    # =====================================================
    # EDIT EVENT
    # =====================================================

    edit_btn.click(

        fn=edit_product,

        inputs=[
            edit_instruction,
            current_product
        ],

        outputs=[
            seo_status,
            title,
            short_description,
            description,
            key_features,
            meta_title,
            meta_description,
            url,
            current_product
        ]
    )


# =========================================================
# اجرا
# =========================================================
import os

port = int(os.environ.get("PORT", 7860))

demo.launch(
    server_name="0.0.0.0",
    server_port=port,
    share=False,
    debug=False
)
