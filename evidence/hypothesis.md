# Giả thuyết — viết TRƯỚC khi tìm bằng chứng (5 phút, commit ngay)

> Điền ở guide bước 1.1. Ôn lại: ngày 2 · lab ngày 2.
> *Ghi chú minh bạch:* Giả thuyết này được nhóm chốt lúc đổi sang Track F ngày 27/11/2026 và bổ sung vào file mẫu lúc 20:33 ngày 27/11/2026 để hoàn thiện hồ sơ CP3.

- **Ngày giờ viết:** 27/11/2026 (chốt hướng Track F trước khi đào data; ghi vào file lúc 20:33 ngày 27/11/2026).
- **Người dùng chính (một vai cụ thể):** Chủ cửa hàng cho thuê áo dài tại Hòa Lạc (trực tiếp tiếp khách và dò lịch thuê trên Google Sheets).
- **Mình nghĩ:** Chủ cửa hàng gặp khó khi kiểm tra nhanh một mẫu áo dài còn hay hết theo từng size trong khoảng ngày khách hỏi vì phải dò thủ công trên Google Sheets nhiều dòng, dễ bỏ sót thời gian giặt qua đêm hoặc dòng ghi thiếu size/ngày, hậu quả là mất thời gian tư vấn và nhận trùng lịch (phải xin lỗi và đổi áo khác cho khách).
- **Có thể còn cách giải thích khác:** Việc nhầm lịch có thể chủ yếu do khách đổi mẫu phút chót mà cửa hàng quên cập nhật trạng thái `HỦY`, chứ không phải do khó dò trên Google Sheets.
- **Mình đúng nếu thấy:** Trên sổ lịch thuê thật của cửa hàng có **≥ 15%** dòng lịch hiệu lực bị thiếu/bất thường dữ liệu (size, ngày giờ, trạng thái) gây rủi ro dò nhầm, hoặc xuất hiện **≥ 3** ca trùng lịch vượt tồn kho trong dữ liệu gần nhất, khớp với phản ánh của chủ cửa hàng.
- **Nguồn sẽ dùng** (≥1 nguồn đạt ngưỡng, guide 1.2): [x] đào data · [x] phỏng vấn kiểm chéo (`P1.md`) · [ ] khảo sát — **nguồn chính:** đào data trên bản trích lịch thuê (`evidence/data-mining.md` + `evidence/count.py`) · **nguồn để kiểm lại:** phỏng vấn trực tiếp chủ cửa hàng (`evidence/interviews/P1.md`).
