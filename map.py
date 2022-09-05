import collections
import torch
from collections import Counter
from iou import Intersection_over_union

def mean_average_precision(
    pred_boxes, true_boxes, iou_threshold=0.5, num_classes=20, box_format='coeners'
):
    epsilon=1e-6
    average_precisions=[]
    
    for i in range(num_classes):
        detections=[ box for box in pred_boxes if box[1]==i]
        ground_truths=[ box for box in true_boxes if box[1]==i]
        
        amount_bboxes= Counter(gt[0] for gt in ground_truths)
        for key, val in amount_bboxes.items():
            amount_bboxes[key] = torch.zeros(val)
        detections.sort(key=lambda x:x[2], reverse=True)
        TP = torch.zeros(len(detections))
        FP = torch.zeros(len(detections))
        total_true_bboxes = len(ground_truths)
        
        for detection_idx, detection in enumerate(detections):
            ground_truth_img=[bbox for bbox in ground_truths if bbox[0]==detection[0]]
            num_gts = len(ground_truth_img)
            best_iou=0
            for idx, gt in enumerate(ground_truth_img):
                iou = Intersection_over_union(
                    torch.tensor(gt[3:]), torch.tensor(detection[3:]),box_format=box_format
                )
                if iou>best_iou:
                    best_iou = iou
                    best_gt_idx = idx
            if best_iou>iou_threshold:
                if amount_bboxes[detection[0]][best_gt_idx]==0:
                    TP[detection_idx] = 1
                    amount_bboxes[detection[0]][best_gt_idx]=1
                else:
                    FP[detection_idx] = 1
            else:
                FP[detection_idx] = 1
        TP_cumsum = torch.cumsum(TP, dim=0)
        FP_cumsum = torch.cumsum(FP, dim=0)
        recalls = TP_cumsum / (total_true_bboxes + epsilon)
        precisions = torch.divide(TP_cumsum,(TP_cumsum + FP_cumsum + epsilon))
        precisions = torch.cat(torch.tensor([1]), precisions)
        recalls = torch.cat(torch.tensor([0]), recalls)
        average_precisions.append(torch.trapz(precisions, recalls))
    return sum(average_precisions) / len(average_precisions)    