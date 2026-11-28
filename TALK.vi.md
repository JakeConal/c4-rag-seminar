# Kịch bản thuyết trình và ghi hình C4 — Tiếng Việt

Recording: pending

Bản tiếng Việt của [TALK.md](TALK.md), dùng cùng [slides.pdf](slides.pdf). Phân công người nói và số liệu giữ theo bản tiếng Anh.

**Kế hoạch ghi hình: 7 phút 45 giây, slide 1–12.** Slide 13–16 dành cho tham khảo và hỏi đáp. Video phải dài không quá tám phút. Các mốc bên dưới là mục tiêu khi tập, chưa phải thời lượng đã kiểm chứng của bản tiếng Việt. Chỉ đọc các đoạn lời thoại; không đọc hướng dẫn, lệnh hoặc phần hỏi đáp. Dành khoảng 20 giây cho thao tác minh họa và chuyển người nói. Tập với đồng hồ, đọc tự nhiên và rút gọn chi tiết nếu vượt thời gian; không cố đọc nhanh cho kịp.

Mở `slides.pdf` và terminal tại thư mục gốc của repository. Chạy trước các lệnh ở phần “Chuẩn bị minh họa bằng log”, tăng cỡ chữ terminal và giữ sẵn kết quả. Khi trình bày, cho xem log đã lưu; replay kiểm tra lại các quan sát đó mà không chạy suy luận mô hình lần nữa.

## Dương Khánh Khải Hưng · 23120045 · Slide 1–4

### Slide 1 · 0:00–0:30 · Câu hỏi nghiên cứu và kết quả chính

Một hệ thống RAG có thể trả lời kém nếu không tìm được bằng chứng phù hợp cho mô hình sinh. Chủ đề của nhóm là chunking và reranking: chia tài liệu và xếp hạng lại bằng chứng. Nhóm kiểm tra liệu xếp hạng lại 50 đoạn đứng đầu có cải thiện năm tài liệu được chọn hay không, và tốn thêm bao nhiêu thời gian. Trên SciFact, MRR tăng 6,15 điểm phần trăm; p95 độ trễ tăng thêm theo cặp khoảng 1,93 giây.

### Slide 2 · 0:30–1:00 · Vị trí của truy xuất trong RAG

Trước khi nhận truy vấn, hệ thống chia tài liệu thành các đoạn và lưu vector embedding của từng đoạn. Khi có truy vấn, hệ thống mã hóa truy vấn, tìm các đoạn ứng viên, có thể xếp hạng lại rồi chọn bằng chứng. Ứng dụng RAG hoàn chỉnh sẽ chuyển bằng chứng cho mô hình sinh. Thí nghiệm của nhóm dừng ở năm mã tài liệu, nên chỉ đánh giá truy xuất, chưa đánh giá chất lượng câu trả lời được sinh ra.

### Slide 3 · 1:00–1:45 · Hai cách chấm mức độ liên quan

Bi-encoder mã hóa truy vấn và từng đoạn riêng biệt. Nhờ vector tài liệu đã lưu, hệ thống có thể tìm kiếm bằng độ tương đồng cosine. Cross-encoder đọc đồng thời truy vấn và đoạn ứng viên, cho các token tương tác rồi chấm điểm liên quan. Mỗi cặp đều cần suy luận mới. Nhóm chấm 50 cặp, thay vì toàn bộ kho tài liệu. Hai phương án dùng cùng 50 đoạn ứng viên. Vì nhiều đoạn có thể thuộc cùng một bản tóm tắt, nhóm duyệt thứ hạng và chỉ giữ năm tài liệu gốc khác nhau. Các đoạn trùng tài liệu không được tính thêm vào recall.

### Slide 4 · 1:45–2:25 · Vì sao ranh giới đoạn quan trọng?

Cấu hình chính dùng cửa sổ 192 token, chồng lấn 32 token; cửa sổ thứ hai bắt đầu ở token 161. Chồng lấn giúp giữ liền một phần nội dung gần ranh giới, nhưng cũng lặp văn bản và tạo thêm vector. Đoạn nhỏ có thể tập trung vào nội dung khớp nhưng mất ngữ cảnh; đoạn lớn giữ ngữ cảnh nhưng chịu giới hạn đầu vào. Có thể chia theo câu, đoạn văn hoặc ngữ nghĩa. Nhóm chỉ thử cửa sổ cố định và giữ nguyên cách chia trong so sánh chính để đo riêng tác động của reranking.

## Nguyễn Minh Hiếu · 23120124 · Slide 5–9

### Slide 5 · 2:25–3:05 · So sánh có kiểm soát

Nhóm chia 5.183 bản tóm tắt SciFact thành 12.434 đoạn và đánh giá trên 300 nhận định kiểm thử. Mỗi nhận định chạy qua cả hai phương án. Nhóm luân phiên thứ tự hai phương án, xáo trộn nhận định qua năm lượt, thu được 1.500 quan sát theo cặp. Mô hình, dữ liệu, số ứng viên và điều kiện CPU được giữ cố định. Mỗi phương án tự mã hóa truy vấn; đo từ bước này đến khi có năm mã tài liệu. Không tính tải dữ liệu, tạo chỉ mục, nạp mô hình và khởi động làm nóng. Năm lượt phản ánh biến động thời gian trên cùng máy, không phải năm bộ dữ liệu độc lập.

### Slide 6 · 3:05–3:40 · Ý nghĩa các chỉ số

Ví dụ minh họa có hai tài liệu liên quan là A và B. Nếu năm kết quả đầu có A ở hạng hai nhưng thiếu B, reciprocal rank bằng một phần hai, recall cũng bằng một phần hai. Đưa A lên hạng nhất thì reciprocal rank bằng một. Tìm thêm được B thì recall bằng một. MRR là trung bình reciprocal rank qua các truy vấn; recall được lấy trung bình từ tỷ lệ tìm được của từng truy vấn. Nếu năm kết quả đầu không có tài liệu liên quan, cả hai chỉ số đều bằng không.

### Slide 7 · 3:40–4:15 · Chất lượng tăng nhưng vẫn có trường hợp giảm

MRR tăng từ 61,05% lên 67,20%; recall tăng từ 73,07% lên 77,72%. Mức tăng tương ứng là 6,15 và 4,64 điểm phần trăm, tính trước khi làm tròn. Thứ hạng giống nhau trong cả năm lượt. Xét từng nhận định, reciprocal rank tăng ở 67 trường hợp, giữ nguyên ở 193 và giảm ở 40. Recall tăng ở 30 và giảm ở 11 trường hợp. Như vậy, reranking cải thiện kết quả chung ở đây, nhưng vẫn có thể đẩy bằng chứng hữu ích xuống thấp.

### Slide 8 · 4:15–5:00 · Chi phí độ trễ

P50 là trung vị thời gian truy vấn; p95 mô tả phần truy vấn chậm hơn. Slide trình bày trung vị của các phân vị qua năm lượt, kèm giá trị nhỏ nhất và lớn nhất. P50 và p95 của phương án gốc là 27,6 và 115,7 mili giây; khi reranking là 1.554,4 và 2.001,0 mili giây. Để tính độ trễ tăng thêm, nhóm lấy thời gian reranking trừ thời gian gốc cho từng truy vấn theo cặp, rồi mới tính phân vị. P95 tăng thêm là 1.928,3 mili giây. Không thể lấy hai p95 trên slide trừ trực tiếp để ra chỉ số này. Trên CPU này, chấm điểm chung chiếm phần lớn thời gian truy xuất.

### Slide 9 · 5:00–5:45 · Kiểm tra bằng chứng từ log

Đây là log của nhận định số 5. Tài liệu liên quan từ hạng tám theo vector lên hạng nhất sau reranking. Nhận định 535 có kết quả ngược lại: từ hạng nhất rơi khỏi năm kết quả đầu. Với nhận định 132, tập ứng viên không có tài liệu được gán nhãn liên quan. Có 32 nhận định gặp tình trạng này. Dù sắp xếp hoàn hảo các tập ứng viên, recall tối đa cũng chỉ đạt 88,63%. Reranker không thể tìm lại bằng chứng chưa có trong đầu vào.

*Thao tác: chuyển sang terminal đã chuẩn bị, chỉ mã tài liệu liên quan của nhận định 5 và hai danh sách xếp hạng, rồi trở lại slide. Dành khoảng 15 giây cho thao tác này. Đây là kiểm tra log đã lưu, không phải lượt đo mới. Tập kỹ phần này để tránh vượt thời gian.*

## Huỳnh Thái Toàn · 23120175 · Slide 10–12

### Slide 10 · 5:45–6:25 · Thí nghiệm bổ sung về chunking

Nhóm còn so sánh cửa sổ 96 token với 192 token, cùng chồng lấn 32 token. Bước trượt giảm từ 160 xuống 64, nên tỷ lệ chồng lấn cũng tăng. Cửa sổ nhỏ tạo 27.090 đoạn, làm ma trận embedding tăng từ 18,21 lên 39,68 MiB. MRR tăng 0,73 điểm phần trăm, recall tăng 1,40 điểm. Mức tăng chất lượng này đi kèm dung lượng ma trận hơn gấp đôi. So sánh bổ sung chỉ dùng truy xuất vector, chưa đo độ trễ hoặc tương tác với reranking.

### Slide 11 · 6:25–7:05 · Giới hạn của kết quả

SciFact gán nhãn cho toàn bộ bản tóm tắt. Một đoạn được truy xuất có thể thuộc tài liệu liên quan nhưng không chứa phần bằng chứng cần thiết. Bằng chứng có thể ủng hộ hoặc bác bỏ nhận định; liên quan không có nghĩa là nhận định đúng. Nhóm chỉ thử một kho dữ liệu, một cặp mô hình và truy vấn tuần tự trên CPU đã làm nóng. Tài liệu chưa được gán nhãn không được tính điểm. Chưa đánh giá người dùng đồng thời, khởi động nguội, phần cứng khác hoặc câu trả lời sinh ra. Vì vậy, khuyến nghị cần được hiểu trong phạm vi này.

### Slide 12 · 7:05–7:45 · Quyết định theo ngân sách độ trễ

Với tải thử nghiệm này, có thể cân nhắc reranking khi lợi ích về thứ hạng xứng đáng với tổng p95 truy xuất khoảng hai giây, chưa tính sinh câu trả lời. Nếu ngân sách chặt hơn, nên giữ thứ tự vector. Nếu thiếu bằng chứng trong tập ứng viên, cần cải thiện truy xuất ban đầu. Đoạn nhỏ hơn là một lựa chọn khác, nhưng mới đo được chi phí lưu trữ, chưa đo thời gian. Bước tiếp theo là thử số ứng viên, bằng chứng ở cấp đoạn và tải thực tế. Repository lưu log gốc, cấu hình cố định và lệnh replay để kiểm tra kết luận.

## Chuẩn bị minh họa bằng log

Chạy trước khi ghi hình. `make replay` tính lại chỉ số và kiểm tra quan sát đã lưu; không chạy suy luận lại và không đo lại độ trễ.

```bash
study_dir=$(cat results/latest-study.txt)
make replay RESULTS="$study_dir"
```

```bash
python3 - <<'PY'
from pathlib import Path
from ragstudy.common import read_json

study = Path(Path("results/latest-study.txt").read_text().strip())
run = read_json(study / "run-01.json")
mapping = read_json(study / "chunk-map.json")
for query_id in ("5", "535", "132"):
    row = next(r for r in run["queries"] if r["query_id"] == query_id)
    pool = list(dict.fromkeys(mapping[c] for c in row["baseline"]["candidates"]))
    rank = next((i for i, doc in enumerate(pool, 1) if doc in row["relevant"]), None)
    print("\nSciFact claim", query_id, row["query"])
    print("Judged relevant:", row["relevant"])
    print("First relevant vector parent rank:", rank or "absent from top-50 pool")
    print("Vector top five:  ", row["baseline"]["docs"])
    print("Reranked top five:", row["reranked"]["docs"])
    print("Individual query latency (ms):",
          f'vector {row["baseline"]["latency_ms"]:.1f}',
          f'reranked {row["reranked"]["latency_ms"]:.1f}')
PY
```

Đoạn lệnh thứ hai đọc lượt đầu đã lưu, ánh xạ đoạn về tài liệu gốc và in thứ hạng thực tế của ba trường hợp. Trong video chỉ cần minh họa trường hợp đầu; giữ sẵn hai trường hợp còn lại để trả lời câu hỏi. Thời gian từng truy vấn là quan sát riêng lẻ, khác với các phân vị tổng hợp ở slide 8. Các nhãn tiếng Anh trong kết quả terminal được giữ để dễ đối chiếu với slide và log.

## Phần trình bày trực tiếp mở rộng · 10 phút, cộng 5 phút hỏi đáp

Chỉ dùng phần này nếu được chọn thuyết trình trực tiếp mười phút. Bắt đầu từ lời thoại chính và thêm các nội dung dưới đây khi tập, hướng tới 9 phút 45 giây để có thời gian chuyển người nói. Bản tiếng Việt vẫn cần được bấm giờ riêng.

- **Hưng: thêm 40 giây sau slide 4.** Dùng sơ đồ cửa sổ để giải thích: một câu đi qua token 192 có thể được giữ liền trong cửa sổ sau, nhưng một đoạn bằng chứng dài hơn phần chồng lấn vẫn có thể bị cắt. Chồng lấn chỉ giảm một số vấn đề ranh giới, không bảo đảm giữ trọn bằng chứng. Đặt câu hỏi: chuyện gì xảy ra khi tiêu đề hoặc định nghĩa ở xa bị tách khỏi câu khớp với truy vấn?
- **Hiếu: thêm 45 giây sau slide 9.** Cho xem trường hợp 535 bị giảm hạng và trường hợp 132 thiếu ứng viên. Phân biệt lỗi thứ hạng, có thể cần bộ chấm điểm tốt hơn, với thiếu ứng viên, cần thay đổi truy xuất. Cho xem kết quả replay và chỉ vào `run-01.json` làm bằng chứng gốc. Chỉ kết luận nguyên nhân ngôn ngữ sau khi thực sự kiểm tra nội dung đoạn văn.
- **Toàn: thêm 35 giây sau slide 12.** Dùng slide phụ lục 14 đề xuất thí nghiệm: thay đổi số ứng viên, giữ cố định cửa sổ, mô hình, máy và truy vấn; đo đồng thời chất lượng, độ bao phủ ứng viên và p50/p95. Sau đó thử riêng các tổ hợp kích thước đoạn và reranker. Đây là đề xuất, chưa có kết quả đo.

Giữ sẵn slide phụ lục 13, 15 và 16 cho câu hỏi về thiết lập, diễn giải và nguồn. Mỗi thành viên cần giải thích được toàn bộ thí nghiệm vì giảng viên có thể hỏi bất kỳ ai.

## Chuẩn bị hỏi đáp · Tất cả thành viên

1. **Vì sao phải chia tài liệu?** Mô hình có giới hạn đầu vào. Chia đoạn giúp truy xuất từng phần nhỏ và biểu diễn các phần riêng biệt. Tuy nhiên, phải quyết định ranh giới và mức lặp nội dung; kích thước đoạn cần được đánh giá bằng thí nghiệm.
2. **Vì sao cross-encoder chậm hơn?** Với bi-encoder, vector của đoạn đã được tính trước. Cross-encoder xử lý lại từng cặp truy vấn–đoạn khi có truy vấn: ở đây là 50 cặp, với kích thước batch 16. Điểm của mô hình dùng để xếp hạng, chưa phải xác suất đã hiệu chỉnh hoặc kết luận đúng sai.
3. **Vì sao chọn 50 ứng viên và năm kết quả?** Đây là số ứng viên và số đầu ra trong câu hỏi đã đăng ký. 50 giới hạn lượng công việc reranking; năm xác định độ sâu đánh giá. Nhóm chưa tối ưu hay chứng minh chúng là lựa chọn tốt nhất. 50 đoạn có thể thuộc ít hơn 50 tài liệu; trung bình đo được là 35,3 tài liệu gốc khác nhau.
4. **Vì sao loại tài liệu gốc trùng nhau?** Nhãn liên quan của SciFact nằm ở cấp tài liệu. Giữ lần xuất hiện đầu tiên của mỗi tài liệu giúp nhiều đoạn chồng lấn chỉ đóng góp một lần trúng. Mọi tập ứng viên đo được đều có ít nhất 18 tài liệu gốc khác nhau, nên mỗi phương án có thể trả về đủ năm tài liệu.
5. **Vì sao chất lượng không dao động giữa các lượt?** Nhóm dùng lại cùng truy vấn, dữ liệu, mô hình và thứ hạng xác định. Thời gian trên máy có thay đổi. Lặp lại giúp mô tả biến động thời gian, chưa đo độ bất định trên truy vấn mới. Nhóm không báo cáo khoảng tin cậy hay kiểm định ý nghĩa thống kê.
6. **Vì sao p95 tăng thêm không bằng p95 reranking trừ p95 gốc?** Phân vị không có tính cộng: hai quan sát ở vị trí p95 có thể thuộc hai truy vấn khác nhau. Nhóm tính chênh lệch thời gian của từng truy vấn theo cặp, lấy p95 trong mỗi lượt rồi tổng hợp qua các lượt.
7. **Kết quả 96 token có chỉ do kích thước đoạn không?** Đây là so sánh hai cấu hình cụ thể với số token chồng lấn cố định. Tỷ lệ chồng lấn tăng từ khoảng 16,7% lên 33,3%, bước trượt giảm và nhiều đoạn hơn cạnh tranh cho 50 vị trí. Một so sánh này chưa tách được tác động của từng yếu tố.
8. **39,68 MiB có phải toàn bộ bộ nhớ ứng dụng không?** Không, đó chỉ là ma trận embedding float32. Mô hình, tokenizer, văn bản và các cấp phát khi chạy cần thêm bộ nhớ. Ma trận chính mất 353,4 giây để tạo, nằm ngoài thời gian truy vấn. Chạy cục bộ không tốn phí API nhưng vẫn dùng tài nguyên tính toán và lưu trữ. MiB là mebibyte, tương đương 1.048.576 byte.
9. **Truy xuất tốt hơn có chứng minh câu trả lời tốt hơn không?** Chưa. Thí nghiệm trả về mã tài liệu và đánh giá bằng nhãn cấp tài liệu. Cần đánh giá riêng bằng chứng trong đoạn và mức độ câu trả lời bám sát bằng chứng. Tài liệu SciFact có thể liên quan vì nó bác bỏ nhận định.
10. **Dùng GPU hoặc cơ sở dữ liệu vector có thay đổi kết quả không?** Có thể thay đổi chi phí và cả thứ hạng, tùy độ chính xác số học và cách tìm kiếm gần đúng. Nhóm đo cosine chính xác và suy luận CPU. Muốn kết luận cho hệ thống triển khai khác phải đo lại có kiểm soát trên hệ thống đó.
11. **Nên cải thiện phần nào trước?** Kiểm tra bằng chứng hữu ích có vào tập ứng viên không. Nếu thiếu, xem lại truy xuất và chunking; nếu có nhưng hạng thấp, xem lại xếp hạng. Tăng số ứng viên, truy xuất kết hợp, chia theo ranh giới và batching đều là giả thuyết cần thử, chưa phải cải thiện đã được chứng minh ở đây.
12. **Người khác tái lập hoặc kiểm tra thế nào?** Làm theo README và chạy `make study` để đo mới. Dùng `make replay RESULTS=...` để kiểm tra log chính đã lưu, và `python3 -m ragstudy.chunk_ablation "$study_dir" --replay` cho so sánh bổ sung. Repository lưu log, phiên bản dữ liệu/mô hình và thông tin môi trường. Độ trễ trên máy khác có thể khác.

## Kiểm tra trước khi hoàn tất video

- Cả ba tập nói thành tiếng; kiểm tra tên và thời điểm chuyển người. Mốc thời gian trong kịch bản chưa chứng minh thời lượng thực tế.
- Ghi đủ ba giọng nói, số liệu chính rõ ràng và phần minh họa log. Dùng slide 1–12; để phụ lục và hỏi đáp cho phần chuẩn bị.
- Kiểm tra video xuất ra dài không quá tám phút, âm thanh rõ và chữ terminal đọc được.
- Tải video lên với quyền ai có liên kết cũng xem được, mở thử khi đã đăng xuất và thay dòng `Recording: pending` bằng liên kết thật. Cập nhật cả trường Recording trong `TALK.md` nếu dùng bản này để ghi hình.
- Rà soát AI log và tự đánh giá theo công việc thực tế. Chuẩn bị xong kịch bản và slide chưa có nghĩa là đã ghi hình hoặc nộp bài.
