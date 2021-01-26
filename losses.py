"""
Created on Mon Jul  3 14:27:26 2017

@author: jimit
"""
################################################ DECLARATIONS ################################################
__author__ 	= 'Jimit Doshi'
__EXEC_NAME__ 	= "losses"

import tensorflow as _tf

EPS = 1e-7

################################################ FUNCTIONS ################################################

### y_true dimensions [b,x,y,c]
### y_pred dimensions [b,x,y,c]

#DEF
#@_tf.function
def get_tp_fp_fn( y_true,y_pred ):
	
	tp = _tf.math.reduce_sum( y_true * y_pred, axis=[1,2] )
	fp = _tf.math.reduce_sum( (1-y_true) * y_pred, axis=[1,2] )
	fn = _tf.math.reduce_sum( y_true * (1-y_pred), axis=[1,2] )
	
	# Shape: [b]
	return tp, fp, fn
#ENDDEF

#DEF
#@_tf.function
def get_iou( y_true,y_pred ):
	
#	tp, fp, fn = get_tp_fp_fn( y_true, y_pred )
#
#	# Shape: [b,c]
#	iou = ( tp + EPS ) / ( tp + fp + fn + EPS )
#	
#	# Shape: [b,c]
#	return iou

	intersection = EPS + _tf.reduce_sum( _tf.multiply( y_pred,y_true ), \
                                        axis=[1,2] )

	union = EPS + _tf.reduce_sum( _tf.subtract( _tf.add( y_pred,y_true ), \
                                                _tf.multiply( y_pred,y_true ) ), \
                                axis=[1,2] )

	iou = _tf.divide( intersection,union )

	# Shape: [b,c]
	return iou
#ENDDEF

#DEF
#@_tf.function
def get_dice( y_true,y_pred ):
	
	tp, fp, fn = get_tp_fp_fn( y_true, y_pred )

	# Shape: [b,c]
	dice = ( 2*tp + EPS ) / ( 2*tp + fp + fn + EPS )

	# Shape: [b,c]
	return dice
#ENDDEF

#DEF
#@_tf.function
def SoftIOULoss( y_true, y_pred ):
	
	iouloss = 1 - get_iou( y_true,y_pred )

	# Shape: []
	return _tf.math.reduce_mean( iouloss )
#ENDDEF

#DEF
#@_tf.function
def FocalIOULoss( y_true, y_pred, gamma=0 ):
	
	focaliouloss = 1 - _tf.math.pow( get_iou( y_true,y_pred ),gamma+1 )

	# Shape: []
	return _tf.math.reduce_mean( focaliouloss )
#ENDDEF

#DEF
#@_tf.function
def SoftDiceLoss( y_true, y_pred ):

	diceloss = 1 - get_dice( y_true,y_pred )

	# Shape: []
	return _tf.math.reduce_mean( diceloss )
#ENDDEF

#DEF
#@_tf.function
def FocalSoftDiceLoss( y_true, y_pred, gamma=0 ):

	focaldiceloss = 1 - _tf.math.pow( get_dice( y_true,y_pred ),gamma+1 )

	# Shape: []
	return _tf.math.reduce_mean( focaldiceloss )
#ENDDEF


#DEF
#@_tf.function
def MAE( y_true, y_pred ):

	mae = _tf.math.abs( y_true-y_pred )

	# Shape: []
	return _tf.math.reduce_mean( mae )
#ENDDEF


#DEF
#@_tf.function
def BCE( y_true, y_pred ):

	bce = -1 * ( y_true*_tf.math.log(EPS + y_pred) \
		+ (1-y_true)*_tf.math.log(EPS + 1-y_pred) )
	
	# Shape: []
	return _tf.math.reduce_mean( bce )
#ENDDEF

#DEF
#@_tf.function
def CombinedLoss( oh,probs,gamma ):

#	iou_mean = FocalIOULoss( oh,probs,gamma )
	iou_mean = SoftIOULoss( oh,probs )
	mae_mean = MAE( oh,probs )
	bce_mean = BCE( oh,probs )

	total_loss_mean = iou_mean + mae_mean + bce_mean

	return total_loss_mean, iou_mean, mae_mean, bce_mean
#ENDDEF

#DEF
#@_tf.function
def getCombinedLoss( oh_d1,probs_d1,probs_d2,probs_d4,gamma,ds,xy ):

	oh_d2 = _tf.image.resize( oh_d1,[int(xy/2),int(xy/2)] )
	oh_d4 = _tf.image.resize( oh_d1,[int(xy/4),int(xy/4)] )

	total_loss_d1, iou_d1, mae_d1, bce_d1 = CombinedLoss( oh_d1,probs_d1,gamma )

	# IF
	if ds:
		total_loss_d2, iou_d2, mae_d2, bce_d2 = CombinedLoss( oh_d2,probs_d2,gamma )
		total_loss_d4, iou_d4, mae_d4, bce_d4 = CombinedLoss( oh_d4,probs_d4,gamma )

		total_loss = total_loss_d1 + 0.5*total_loss_d2 + 0.25*total_loss_d4
	else:
		total_loss = total_loss_d1
	# ENDIF

	return total_loss, total_loss_d1, iou_d1, mae_d1, bce_d1
#ENDDEF

